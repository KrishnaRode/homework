"""Child-safety and quality guardrails. Local, deterministic, no external calls."""
from __future__ import annotations

from typing import Any

from .. import config

# Words/themes that must never appear in content for children.
_BANNED = [
    "sex", "porn", "nude", "kill", "suicide", "drugs", "cocaine", "heroin",
    "gun", "weapon", "terror", "rape", "abuse", "gambling", "alcohol",
    "cigarette", "violence", "blood", "gore", "politics", "election",
]

SYSTEM_SAFETY = (
    "You are PrepWell, a kind and encouraging AI tutor for school children. "
    "Always use grade-appropriate, simple, positive language. Never produce "
    "harmful, adult, violent, political, or scary content. Be supportive and "
    "never insulting. Output must be valid JSON only."
)


def text_is_safe(text: str) -> bool:
    low = (text or "").lower()
    return not any(bad in low for bad in _BANNED)


def question_is_valid(q: dict[str, Any], klass: str, subject: str) -> tuple[bool, str]:
    """Quality + safety gate for a generated question. Returns (ok, reason)."""
    if not isinstance(q, dict):
        return False, "not an object"
    question_text = str(q.get("question", "")).strip()
    if len(question_text) < 8:
        return False, "question too short"
    blob = " ".join(
        str(q.get(k, "")) for k in ("question", "explanation", "how_to_think", "common_mistake")
    ) + " ".join(str(o) for o in q.get("options", []) or [])
    if not text_is_safe(blob):
        return False, "failed safety check"
    qtype = q.get("type", "mcq")
    if qtype == "mcq":
        opts = q.get("options") or []
        if len(opts) < 2:
            return False, "mcq needs >=2 options"
    try:
        diff = int(q.get("difficulty", 3))
    except (TypeError, ValueError):
        return False, "bad difficulty"
    if not 1 <= diff <= 5:
        return False, "difficulty out of range"
    if subject not in config.SUBJECTS:
        return False, "unknown subject"
    return True, "ok"


def coerce_question(q: dict[str, Any], *, klass: str, subject: str, topic: str) -> dict[str, Any]:
    """Force a model output into a guaranteed-valid question shape."""
    qtype = q.get("type", "mcq")
    if qtype not in config.QUESTION_TYPES:
        qtype = "short_answer"
    options = q.get("options") or []
    if not isinstance(options, list):
        options = []
    options = [str(o) for o in options][:6]
    try:
        difficulty = max(1, min(5, int(q.get("difficulty", 3))))
    except (TypeError, ValueError):
        difficulty = 3
    return {
        "class": klass,
        "subject": subject,
        "topic": q.get("topic") or topic,
        "difficulty": difficulty,
        "type": qtype,
        "question": str(q.get("question", "")).strip(),
        "options": options,
        "expected_answer": str(q.get("expected_answer", "")).strip(),
        "explanation": str(q.get("explanation", "")).strip(),
        "how_to_think": str(q.get("how_to_think", "")).strip(),
        "common_mistake": str(q.get("common_mistake", "")).strip(),
        "skill_tags": [str(s) for s in (q.get("skill_tags") or [])][:6],
        "estimated_time_seconds": int(q.get("estimated_time_seconds", 60) or 60),
    }
