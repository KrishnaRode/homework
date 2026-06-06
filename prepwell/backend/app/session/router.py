"""The adaptive learning loop: start -> next -> answer -> stop/summary."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from .. import config
from ..auth.deps import require_student
from ..evaluation import service as evaluation
from ..mental_model import service as mm
from ..ollama_client import client as ollama
from ..question_engine import service as engine
from ..schemas import (
    AnswerRequest,
    NextQuestionRequest,
    StartSessionRequest,
    StartSessionResponse,
)
from ..storage import db, files
from ..syllabus import service as syllabus

router = APIRouter(prefix="/api/session", tags=["session"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _own_session(session_id: str, student_id: str) -> dict[str, Any]:
    session = db.get_session(session_id)
    if not session or session["student_id"] != student_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return session


def _public_view(q: dict[str, Any], answered_total: int) -> dict[str, Any]:
    """Student-safe view of a question (no answer leakage). Passage/set fields ride
    along so the frontend can show the reading passage above the question."""
    public = {
        k: v
        for k, v in q.items()
        if k not in ("expected_answer", "explanation", "how_to_think", "common_mistake")
    }
    public["index"] = answered_total + 1
    public["limit"] = config.MAX_QUESTIONS
    return public


def _set_size(klass: str) -> int:
    digits = "".join(ch for ch in str(klass) if ch.isdigit())
    n = int(digits) if digits else 5
    return 3 if n <= 4 else 4 if n <= 8 else 5


def _pick_topic(student_id: str, klass: str, subject: str, board: str, adaptive: bool, requested: str | None) -> str | None:
    if not adaptive and requested:
        return requested
    # Adaptive: practice the weakest known topic, else first syllabus topic.
    model = mm.get_or_create(student_id)
    for key in model.get("recommended_next_topics", []):
        if key.startswith(subject.lower() + "."):
            return key.split(".", 1)[1]
    topics = syllabus.topics_for(klass, subject, board)
    return topics[0]["topic_id"] if topics else None


@router.post("/start", response_model=StartSessionResponse)
def start(req: StartSessionRequest, user: dict = Depends(require_student)) -> StartSessionResponse:
    student = db.get_student(user["student_id"])
    if not student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    if req.subject not in config.SUBJECTS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown subject {req.subject}")
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    db.create_session(session_id, user["student_id"], req.subject, req.topic, req.adaptive, _now())
    return StartSessionResponse(
        session_id=session_id, subject=req.subject, topic=req.topic, adaptive=req.adaptive
    )


@router.post("/next")
def next_question(req: NextQuestionRequest, user: dict = Depends(require_student)) -> dict[str, Any]:
    session = _own_session(req.session_id, user["student_id"])
    if session.get("ended_at"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session already ended")
    if session["total"] >= config.MAX_QUESTIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session question limit reached")

    # Serve any question already queued from a multi-question set (e.g. the rest of a
    # reading-comprehension passage) before generating a new one. The background
    # prefetch naturally drains this queue, so the passage's questions flow in order.
    queued = files.pop_cache(req.session_id)
    if queued:
        return _public_view(queued, session["total"])

    student = db.get_student(user["student_id"])
    board = student.get("board", "cbse")
    topic_id = _pick_topic(
        user["student_id"], student["class"], session["subject"],
        board, bool(session["adaptive"]), session["topic"],
    )
    topic = syllabus.find_topic(student["class"], session["subject"], topic_id, board)
    try:
        if topic and engine.is_comprehension_topic(topic):
            qset = engine.generate_comprehension_set(
                student_id=user["student_id"],
                klass=student["class"],
                board=board,
                subject=session["subject"],
                topic=topic,
                count=_set_size(student["class"]),
                session_id=req.session_id,
            )
            for extra in qset[1:]:
                files.push_cache(req.session_id, extra)
            return _public_view(qset[0], session["total"])

        q = engine.generate_question(
            student_id=user["student_id"],
            klass=student["class"],
            board=board,
            subject=session["subject"],
            topic_id=topic_id,
            turn_index=session["total"],
        )
    except ollama.OllamaUnavailable:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "PrepWell needs Ollama running locally. Start it using: ollama serve",
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))

    return _public_view(q, session["total"])


@router.post("/answer")
def answer(req: AnswerRequest, user: dict = Depends(require_student)) -> dict[str, Any]:
    session = _own_session(req.session_id, user["student_id"])
    question = files.load_question(user["student_id"], req.question_id)
    if not question:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    result = evaluation.evaluate(
        student_id=user["student_id"],
        question=question,
        answer=req.answer,
        time_taken=req.time_taken_seconds,
        used_hint=req.used_hint,
    )
    db.record_answer_in_session(req.session_id, bool(result["correct"]), int(result["score"]))
    db.mark_asked_result(user["student_id"], req.question_id, bool(result["correct"]), int(result["score"]))
    return result


@router.post("/stop")
def stop(req: NextQuestionRequest, user: dict = Depends(require_student)) -> dict[str, Any]:
    session = _own_session(req.session_id, user["student_id"])
    if not session.get("ended_at"):
        db.end_session(req.session_id, _now())
    return summary(req.session_id, user)


@router.get("/{session_id}/summary")
def summary(session_id: str, user: dict = Depends(require_student)) -> dict[str, Any]:
    session = _own_session(session_id, user["student_id"])
    total = session["total"]
    correct = session["correct"]
    mm_summary = mm.summary(user["student_id"])
    return {
        "session_id": session_id,
        "subject": session["subject"],
        "total_questions": total,
        "correct": correct,
        "accuracy": round(100 * correct / total, 1) if total else 0.0,
        "avg_score": round(session["score_sum"] / total, 1) if total else 0.0,
        "strengths": mm_summary["strengths"],
        "weak_areas": mm_summary["weak_areas"],
        "recommended_next_topics": mm_summary["recommended_next_topics"],
        "overall_index": mm_summary["overall_index"],
    }
