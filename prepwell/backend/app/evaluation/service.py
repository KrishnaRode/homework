"""Answer evaluation: deterministic where possible, LLM rubric otherwise.

After grading, the student's mental model is updated and the next difficulty/type
are derived from it.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from ..guardrails import service as guardrails
from ..mental_model import service as mm
from ..ollama_client import client as ollama
from . import prompts

_OBJECTIVE_TYPES = {"mcq", "fill_blank", "short_answer", "true_false_reason"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _numbers(s: str) -> list[str]:
    return re.findall(r"-?\d+(?:\.\d+)?", s or "")


def _objective_match(question: dict[str, Any], answer: str) -> Optional[bool]:
    """Return True/False for a confident deterministic match, or None if unsure."""
    expected = question.get("expected_answer", "")
    qtype = question.get("type")
    a, e = _norm(answer), _norm(expected)
    if not a:
        return False
    if qtype == "mcq":
        if a == e:
            return True
        # Allow matching by option letter (a/b/c/d) or option text.
        opts = question.get("options", [])
        for i, opt in enumerate(opts):
            letter = chr(ord("a") + i)
            if _norm(opt) == e and (a == letter or a == _norm(opt)):
                return True
        return a == e
    if qtype in ("short_answer", "fill_blank"):
        en, an = _numbers(expected), _numbers(answer)
        if en and an:
            return en == an
        if e and (a == e or e in a or a in e):
            return True
        return None  # let the LLM judge wording
    if qtype == "true_false_reason":
        exp_tf = "true" in e or e.startswith("t")
        ans_tf = "true" in a or a.strip() in ("t", "yes")
        # Correct only if the boolean matches; reason quality refined by LLM.
        return exp_tf == ans_tf if ("true" in a or "false" in a) else None
    return None


def _fallback_eval(question: dict[str, Any], correct: bool) -> dict[str, Any]:
    return {
        "correct": correct,
        "score": 100 if correct else 25,
        "what_was_right": "You answered the question." if correct else "You gave it a try — that matters.",
        "what_was_wrong": "" if correct else "The answer wasn't quite right this time.",
        "step_by_step": [s for s in [question.get("how_to_think", "")] if s],
        "how_to_think": question.get("how_to_think", ""),
        "misconception": None if correct else question.get("common_mistake") or None,
        "encouragement": "Great work!" if correct else "Keep going — every mistake is a step forward.",
    }


def evaluate(
    *,
    student_id: str,
    question: dict[str, Any],
    answer: str,
    time_taken: int,
    used_hint: bool,
) -> dict[str, Any]:
    qtype = question.get("type", "mcq")
    deterministic = _objective_match(question, answer) if qtype in _OBJECTIVE_TYPES else None

    if deterministic is not None and qtype == "mcq":
        result = _fallback_eval(question, deterministic)
        result["score"] = 100 if deterministic else 0
        result["what_was_right"] = (
            "Correct! You picked the right option." if deterministic else ""
        )
        result["what_was_wrong"] = (
            "" if deterministic else f"The correct answer was: {question.get('expected_answer')}."
        )
    else:
        # Use the LLM rubric (with deterministic hint folded in when available).
        try:
            raw = ollama.generate_json(
                prompts.build_eval_prompt(question, answer),
                system=guardrails.SYSTEM_SAFETY,
                temperature=0.2,
            )
            result = {
                "correct": bool(raw.get("correct", False)),
                "score": max(0, min(100, int(raw.get("score", 0) or 0))),
                "what_was_right": str(raw.get("what_was_right", "")),
                "what_was_wrong": str(raw.get("what_was_wrong", "")),
                "step_by_step": [str(s) for s in (raw.get("step_by_step") or [])][:8],
                "how_to_think": str(raw.get("how_to_think") or question.get("how_to_think", "")),
                "misconception": (str(raw["misconception"]) if raw.get("misconception") else None),
                "encouragement": str(raw.get("encouragement", "Nice effort!")),
            }
            if deterministic is not None:
                result["correct"] = deterministic
                if deterministic and result["score"] < 60:
                    result["score"] = 75
        except (ollama.OllamaUnavailable, ValueError):
            result = _fallback_eval(question, bool(deterministic))

    if not result.get("step_by_step"):
        result["step_by_step"] = [s for s in [question.get("how_to_think", "")] if s]
    result["expected_answer"] = question.get("expected_answer", "")

    # Update the mental model (the heart) and derive what comes next.
    model = mm.update_after_answer(
        student_id,
        subject=question.get("subject"),
        topic_id=question.get("topic_id") or question.get("topic"),
        topic_title=question.get("topic"),
        difficulty=int(question.get("difficulty", 3)),
        correct=bool(result["correct"]),
        score=int(result["score"]),
        time_taken=time_taken,
        est_time=int(question.get("estimated_time_seconds", 60)),
        used_hint=used_hint,
        question_type=qtype,
        misconception=result.get("misconception"),
        question_hash=question.get("question_hash", ""),
    )
    result["next_difficulty"] = mm.next_difficulty_for(
        model, question.get("subject"), question.get("topic_id") or question.get("topic")
    )
    result["next_type"] = "step_problem" if not result["correct"] else "mcq"
    return result
