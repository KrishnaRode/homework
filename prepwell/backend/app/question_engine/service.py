"""Question generation: build prompt -> Ollama -> validate -> de-duplicate -> persist."""
from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from .. import config
from ..guardrails import service as guardrails
from ..mental_model import service as mm
from ..ollama_client import client as ollama
from ..storage import db, files
from ..syllabus import service as syllabus
from . import prompts

# Question-type rotation so we never ask only MCQs.
_TYPE_CYCLE = [
    "mcq", "short_answer", "fill_blank", "word_problem", "true_false_reason",
    "explain", "step_problem", "reasoning", "spot_mistake", "match",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def question_hash(subject: str, topic_id: str, question_text: str) -> str:
    raw = f"{subject.lower()}|{topic_id}|{_normalize(question_text)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def is_comprehension_topic(topic: dict[str, Any]) -> bool:
    """A reading-comprehension topic needs a shared passage + a set of questions."""
    blob = " ".join(
        [
            str(topic.get("topic_id", "")),
            str(topic.get("title", "")),
            " ".join(str(s) for s in topic.get("skills", []) or []),
        ]
    ).lower()
    return "comprehension" in blob or "passage" in blob


def choose_type(model: dict[str, Any], turn_index: int, forced: Optional[str] = None) -> str:
    if forced and forced in config.QUESTION_TYPES:
        return forced
    # If the student is slow/struggling, favor lighter, more engaging types.
    if model.get("confidence_index", 50) < 40 and turn_index % 3 == 0:
        return "word_problem"
    return _TYPE_CYCLE[turn_index % len(_TYPE_CYCLE)]


def generate_question(
    *,
    student_id: str,
    klass: str,
    subject: str,
    topic_id: Optional[str],
    board: str = "cbse",
    difficulty: Optional[int] = None,
    qtype: Optional[str] = None,
    turn_index: int = 0,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Generate one validated, non-duplicate question and persist it.

    Raises ollama.OllamaUnavailable if the local model server is down.
    """
    topic = syllabus.find_topic(klass, subject, topic_id, board)
    if not topic:
        raise ValueError(f"No syllabus topic for class {klass} {subject} / {topic_id}")

    model = mm.get_or_create(student_id)
    diff = difficulty or mm.next_difficulty_for(model, subject, topic["topic_id"])
    chosen_type = choose_type(model, turn_index, qtype)

    tm = mm.topic_mastery(model, mm.topic_key(subject, topic["topic_id"])) or {}
    wrong_patterns = tm.get("wrong_patterns", [])
    seen = db.asked_hashes(student_id)

    recent_texts = [h.get("topic", "") for h in db.question_history(student_id, limit=8)]

    last_error = "unknown"
    for attempt in range(max_attempts):
        prompt = prompts.build_generation_prompt(
            klass=klass,
            board=syllabus.board_label(board),
            subject=subject,
            topic=topic,
            difficulty=diff,
            qtype=chosen_type,
            wrong_patterns=wrong_patterns,
            avoid_questions=recent_texts,
        )
        raw = ollama.generate_json(
            prompt,
            system=guardrails.SYSTEM_SAFETY,
            temperature=0.8 if attempt == 0 else 0.5,
        )
        q = guardrails.coerce_question(raw, klass=klass, subject=subject, topic=topic["title"])
        ok, reason = guardrails.question_is_valid(q, klass, subject)
        if not ok:
            last_error = reason
            continue
        qhash = question_hash(subject, topic["topic_id"], q["question"])
        if qhash in seen:
            last_error = "duplicate"
            chosen_type = _TYPE_CYCLE[(turn_index + attempt + 1) % len(_TYPE_CYCLE)]
            continue
        # Success.
        q["question_id"] = f"q_{uuid.uuid4().hex[:12]}"
        q["question_hash"] = qhash
        q["topic_id"] = topic["topic_id"]
        files.append_question(student_id, q)
        db.record_asked(
            student_id, qhash, q["question_id"], session_id="",
            subject=subject, topic=topic["topic_id"], difficulty=diff,
            qtype=chosen_type, asked_at=_now(),
        )
        return q

    raise ValueError(f"Could not generate a valid unique question (last issue: {last_error})")


def generate_comprehension_set(
    *,
    student_id: str,
    klass: str,
    subject: str,
    topic: dict[str, Any],
    board: str = "cbse",
    difficulty: Optional[int] = None,
    count: int = 4,
    session_id: str = "",
    max_attempts: int = 3,
) -> list[dict[str, Any]]:
    """Generate ONE passage plus a set of questions on it, all persisted and sharing
    a passage_id. Returns the questions in order (caller serves the first and queues
    the rest). Raises ollama.OllamaUnavailable if the model server is down.
    """
    model = mm.get_or_create(student_id)
    diff = difficulty or mm.next_difficulty_for(model, subject, topic["topic_id"])
    seen = db.asked_hashes(student_id)

    last_error = "unknown"
    for attempt in range(max_attempts):
        prompt = prompts.build_comprehension_prompt(
            klass=klass,
            board=syllabus.board_label(board),
            subject=subject,
            topic=topic,
            difficulty=diff,
            count=count,
        )
        raw = ollama.generate_json(
            prompt,
            system=guardrails.SYSTEM_SAFETY,
            temperature=0.8 if attempt == 0 else 0.5,
        )
        passage = str((raw or {}).get("passage", "")).strip()
        items = (raw or {}).get("questions") or []
        if len(passage) < 40 or not isinstance(items, list) or len(items) < 2:
            last_error = "incomplete passage set"
            continue
        if not guardrails.text_is_safe(passage):
            last_error = "passage failed safety check"
            continue

        passage_id = f"psg_{uuid.uuid4().hex[:10]}"
        prepared: list[tuple[dict[str, Any], str]] = []
        for raw_q in items:
            q = guardrails.coerce_question(raw_q, klass=klass, subject=subject, topic=topic["title"])
            q["difficulty"] = diff
            ok, reason = guardrails.question_is_valid(q, klass, subject)
            if not ok:
                last_error = reason
                continue
            qhash = question_hash(subject, topic["topic_id"], q["question"])
            if qhash in seen:
                last_error = "duplicate"
                continue
            seen.add(qhash)
            prepared.append((q, qhash))

        if len(prepared) < 2:
            last_error = "too few valid questions in set"
            continue

        total = len(prepared)
        out: list[dict[str, Any]] = []
        for idx, (q, qhash) in enumerate(prepared):
            q["question_id"] = f"q_{uuid.uuid4().hex[:12]}"
            q["question_hash"] = qhash
            q["topic_id"] = topic["topic_id"]
            q["passage"] = passage
            q["passage_id"] = passage_id
            q["set_index"] = idx + 1
            q["set_total"] = total
            files.append_question(student_id, q)
            db.record_asked(
                student_id, qhash, q["question_id"], session_id=session_id,
                subject=subject, topic=topic["topic_id"], difficulty=diff,
                qtype=q["type"], asked_at=_now(),
            )
            out.append(q)
        return out

    raise ValueError(f"Could not generate a comprehension set (last issue: {last_error})")
