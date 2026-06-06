"""JSON-file storage for mental models, full question objects, and the gen cache."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .. import config


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# ---- mental models ----
def mental_model_path(student_id: str) -> Path:
    return config.STUDENTS_DIR / f"{student_id}.json"


def load_mental_model(student_id: str) -> Optional[dict[str, Any]]:
    return _read_json(mental_model_path(student_id))


def save_mental_model(student_id: str, model: dict[str, Any]) -> None:
    _write_json(mental_model_path(student_id), model)


# ---- full question objects (per student, append to a history file) ----
def question_log_path(student_id: str) -> Path:
    return config.HISTORY_DIR / f"{student_id}.jsonl"


def append_question(student_id: str, question: dict[str, Any]) -> None:
    path = question_log_path(student_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(question, ensure_ascii=False) + "\n")


def load_question(student_id: str, question_id: str) -> Optional[dict[str, Any]]:
    path = question_log_path(student_id)
    if not path.exists():
        return None
    found = None
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("question_id") == question_id:
                found = obj
    return found


# ---- generation cache (pre-generated next questions per session) ----
def cache_path(session_id: str) -> Path:
    return config.CACHE_DIR / f"{session_id}.json"


def load_cache(session_id: str) -> list[dict[str, Any]]:
    data = _read_json(cache_path(session_id))
    return data.get("queue", []) if data else []


def save_cache(session_id: str, queue: list[dict[str, Any]]) -> None:
    _write_json(cache_path(session_id), {"queue": queue})


def push_cache(session_id: str, question: dict[str, Any]) -> None:
    queue = load_cache(session_id)
    queue.append(question)
    save_cache(session_id, queue)


def pop_cache(session_id: str) -> Optional[dict[str, Any]]:
    queue = load_cache(session_id)
    if not queue:
        return None
    item = queue.pop(0)
    save_cache(session_id, queue)
    return item
