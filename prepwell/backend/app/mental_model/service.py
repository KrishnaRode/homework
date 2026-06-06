"""The student mental model: the heart of PrepWell's personalization.

Stored as one JSON file per student in data/students/<id>.json. Updated after every
answer with accuracy, speed, confidence, reasoning, and per-topic mastery, then used to
choose the next difficulty and question type.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from ..storage import db, files


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def topic_key(subject: str, topic_id: str) -> str:
    return f"{subject.lower()}.{topic_id}"


def _default_brain() -> dict[str, Any]:
    """Standalone Brain-Games stats. Intentionally separate from the academic
    indices so playing reasoning games never inflates the learning metrics."""
    return {
        "points": 0,
        "games_played": 0,
        "current_streak": 0,
        "best_streak": 0,
        "by_game": {},
        "last_played": None,
    }


def default_model(student_id: str, name: str, klass: str, board: str = "cbse") -> dict[str, Any]:
    return {
        "student_id": student_id,
        "name": name,
        "class": klass,
        "board": board,
        "overall_index": 50,
        "confidence_index": 50,
        "speed_index": 50,
        "accuracy_index": 50,
        "reasoning_index": 50,
        "topic_mastery": {},
        "learning_style": {
            "prefers_visual": False,
            "needs_step_by_step": True,
            "gets_fast_questions_wrong": False,
        },
        "recent_mistakes": [],
        "recommended_next_topics": [],
        "brain": _default_brain(),
    }


def get_or_create(student_id: str) -> dict[str, Any]:
    model = files.load_mental_model(student_id)
    if model:
        return model
    student = db.get_student(student_id)
    name = student["name"] if student else student_id
    klass = student["class"] if student else "5"
    board = student.get("board", "cbse") if student else "cbse"
    model = default_model(student_id, name, klass, board)
    files.save_mental_model(student_id, model)
    return model


def _ema(old: float, new: float, alpha: float = 0.25) -> int:
    return round(old * (1 - alpha) + new * alpha)


def topic_mastery(model: dict[str, Any], key: str) -> dict[str, Any]:
    return model.get("topic_mastery", {}).get(key)


def next_difficulty_for(model: dict[str, Any], subject: str, topic_id: str) -> int:
    tm = topic_mastery(model, topic_key(subject, topic_id))
    if tm and isinstance(tm.get("next_difficulty"), int):
        return max(1, min(5, tm["next_difficulty"]))
    # Cold start: derive from overall accuracy.
    acc = model.get("accuracy_index", 50)
    return 1 if acc < 30 else 2 if acc < 55 else 3 if acc < 75 else 4


def update_after_answer(
    student_id: str,
    *,
    subject: str,
    topic_id: str,
    topic_title: str,
    difficulty: int,
    correct: bool,
    score: int,
    time_taken: int,
    est_time: int,
    used_hint: bool,
    question_type: str,
    misconception: Optional[str],
    question_hash: str,
) -> dict[str, Any]:
    """Apply one answer to the mental model and persist it. Returns the model."""
    model = get_or_create(student_id)
    key = topic_key(subject, topic_id)
    tm = model["topic_mastery"].get(key) or {
        "title": topic_title,
        "mastery": 50,
        "attempts": 0,
        "correct": 0,
        "wrong_patterns": [],
        "last_seen": None,
        "next_difficulty": difficulty,
        "repeat_lock": [],
    }

    tm["attempts"] += 1
    tm["correct"] += 1 if correct else 0
    tm["mastery"] = _ema(tm["mastery"], score)
    tm["last_seen"] = _now()
    if question_hash and question_hash not in tm["repeat_lock"]:
        tm["repeat_lock"].append(question_hash)
        tm["repeat_lock"] = tm["repeat_lock"][-200:]

    # Adaptive next difficulty: fast+correct climbs slowly, struggle drops faster.
    fast = est_time and time_taken and time_taken <= est_time * 0.6
    if correct and score >= 70:
        tm["next_difficulty"] = min(5, difficulty + (1 if fast else 0) or difficulty)
        if fast:
            tm["next_difficulty"] = min(5, difficulty + 1)
    elif not correct or score < 40:
        tm["next_difficulty"] = max(1, difficulty - 1)
    else:
        tm["next_difficulty"] = difficulty

    if misconception and not correct:
        pat = misconception.strip()[:80]
        if pat and pat not in tm["wrong_patterns"]:
            tm["wrong_patterns"] = (tm["wrong_patterns"] + [pat])[-6:]
        model["recent_mistakes"] = (
            model.get("recent_mistakes", []) + [{"topic": topic_title, "issue": pat, "at": _now()}]
        )[-10:]

    model["topic_mastery"][key] = tm

    # Roll global indices.
    model["accuracy_index"] = _ema(model["accuracy_index"], 100 if correct else 0)
    if est_time and time_taken:
        speed_score = 100 if time_taken <= est_time else max(0, 100 - (time_taken - est_time) * 2)
        model["speed_index"] = _ema(model["speed_index"], min(100, speed_score))
    conf_signal = score if not used_hint else max(0, score - 15)
    model["confidence_index"] = _ema(model["confidence_index"], conf_signal)
    if question_type in ("reasoning", "step_problem", "word_problem", "explain", "spot_mistake"):
        model["reasoning_index"] = _ema(model["reasoning_index"], score)

    model["learning_style"]["gets_fast_questions_wrong"] = bool(fast and not correct)

    model["overall_index"] = round(
        0.4 * model["accuracy_index"]
        + 0.2 * model["confidence_index"]
        + 0.2 * model["reasoning_index"]
        + 0.2 * model["speed_index"]
    )

    model["recommended_next_topics"] = _recommend(model)
    files.save_mental_model(student_id, model)
    return model


def _recommend(model: dict[str, Any], limit: int = 3) -> list[str]:
    """Weakest-mastery topics first; these are what the student should practice next."""
    ranked = sorted(
        model.get("topic_mastery", {}).items(),
        key=lambda kv: kv[1].get("mastery", 50),
    )
    return [k for k, _ in ranked[:limit]]


def brain_stats(student_id: str) -> dict[str, Any]:
    """Read-only Brain-Games stats for a student (never affects academic indices)."""
    model = get_or_create(student_id)
    return model.get("brain") or _default_brain()


def record_game_result(
    student_id: str,
    *,
    game: str,
    score: int,
    won: bool,
    duration_seconds: int = 0,
) -> dict[str, Any]:
    """Apply one Brain-Game result to the standalone brain stats. Returns brain stats.

    This deliberately does NOT touch overall_index / reasoning_index etc. — Brain Games
    are a separate, just-for-reasoning track.
    """
    model = get_or_create(student_id)
    brain = model.get("brain") or _default_brain()
    score = max(0, min(100, int(score)))

    brain["games_played"] = brain.get("games_played", 0) + 1
    brain["points"] = brain.get("points", 0) + score
    if won:
        brain["current_streak"] = brain.get("current_streak", 0) + 1
        brain["best_streak"] = max(brain.get("best_streak", 0), brain["current_streak"])
    else:
        brain["current_streak"] = 0

    by = brain.setdefault("by_game", {})
    g = by.get(game) or {"played": 0, "best": 0, "wins": 0}
    g["played"] += 1
    g["best"] = max(g.get("best", 0), score)
    g["wins"] = g.get("wins", 0) + (1 if won else 0)
    by[game] = g

    brain["last_played"] = _now()
    model["brain"] = brain
    files.save_mental_model(student_id, model)
    return brain


def summary(student_id: str) -> dict[str, Any]:
    model = get_or_create(student_id)
    masteries = model.get("topic_mastery", {})
    strengths = [v.get("title", k) for k, v in masteries.items() if v.get("mastery", 0) >= 75]
    weak = [v.get("title", k) for k, v in masteries.items() if v.get("mastery", 100) < 55]
    return {
        "student_id": student_id,
        "name": model.get("name"),
        "class": model.get("class"),
        "board": model.get("board", "cbse"),
        "overall_index": model.get("overall_index"),
        "accuracy_index": model.get("accuracy_index"),
        "confidence_index": model.get("confidence_index"),
        "speed_index": model.get("speed_index"),
        "reasoning_index": model.get("reasoning_index"),
        "strengths": strengths[:5],
        "weak_areas": weak[:5],
        "recommended_next_topics": model.get("recommended_next_topics", []),
        "topic_mastery": masteries,
        "recent_mistakes": model.get("recent_mistakes", []),
    }
