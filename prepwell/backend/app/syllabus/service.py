"""Syllabus loading + lookups — board-aware.

Resolution order for (board, class, subject):
  1. Board-specific override file:  data/syllabus/<board>_class<N>_<subject>.json
  2. Curriculum override file:      data/syllabus/curricula/<curriculum>/class<N>_<subject>.json
  3. In-code curriculum:            curriculum_data.CURRICULUM[<curriculum>][Subject][<N>]
  4. Fallback to the "ncert" curriculum (most boards follow it).

Drop a JSON file matching pattern (1) or (2) to override any cell with no code change
(keeps the README's "drop a normalized JSON" promise). PrepWell never scrapes at runtime.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from .. import config
from . import curriculum_data as cd

DEFAULT_BOARD = cd.DEFAULT_BOARD
DEFAULT_CURRICULUM = cd.DEFAULT_CURRICULUM


# ---- board helpers ----------------------------------------------------------
def boards() -> list[dict[str, str]]:
    return cd.BOARDS


def _board_index() -> dict[str, dict[str, str]]:
    return {b["code"]: b for b in cd.BOARDS}


def normalize_board(board: Optional[str]) -> str:
    if board and board.lower() in _board_index():
        return board.lower()
    return DEFAULT_BOARD


def get_board(board: Optional[str]) -> dict[str, str]:
    return _board_index().get(normalize_board(board), _board_index()[DEFAULT_BOARD])


def curriculum_for_board(board: Optional[str]) -> str:
    cur = get_board(board).get("curriculum", DEFAULT_CURRICULUM)
    return cur if cur in cd.CURRICULUM else DEFAULT_CURRICULUM


def board_label(board: Optional[str]) -> str:
    return get_board(board).get("name", "CBSE")


# ---- subject helpers --------------------------------------------------------
def normalize_subject(subject: Optional[str]) -> Optional[str]:
    if not subject:
        return None
    for s in config.SUBJECTS:
        if s.lower() == subject.lower():
            return s
    return None


# ---- syllabus resolution ----------------------------------------------------
def _read_json(path) -> Optional[dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _from_files(board: str, curriculum: str, klass: str, subject: str) -> Optional[dict[str, Any]]:
    subj_lower = subject.lower()
    candidates = [
        config.SYLLABUS_DIR / f"{board}_class{klass}_{subj_lower}.json",
        config.SYLLABUS_DIR / "curricula" / curriculum / f"class{klass}_{subj_lower}.json",
        config.SYLLABUS_DIR / f"class{klass}_{subj_lower}.json",  # legacy flat files
    ]
    for path in candidates:
        if path.exists():
            data = _read_json(path)
            if data and data.get("chapters"):
                return data
    return None


def _from_code(curriculum: str, klass: str, subject: str) -> Optional[list[dict[str, Any]]]:
    for cur in (curriculum, DEFAULT_CURRICULUM):
        chapters = cd.CURRICULUM.get(cur, {}).get(subject, {}).get(klass)
        if chapters:
            return chapters
    return None


def get_syllabus(klass: str, subject: str, board: Optional[str] = None) -> Optional[dict[str, Any]]:
    subject = normalize_subject(subject)
    if not subject:
        return None
    board = normalize_board(board)
    curriculum = curriculum_for_board(board)

    override = _from_files(board, curriculum, klass, subject)
    if override:
        override.setdefault("class", klass)
        override.setdefault("subject", subject)
        override.setdefault("board", board)
        return override

    chapters = _from_code(curriculum, klass, subject)
    if not chapters:
        return None
    return {
        "class": klass,
        "subject": subject,
        "board": board,
        "curriculum": curriculum,
        "source": "ncert" if curriculum == DEFAULT_CURRICULUM else curriculum,
        "chapters": chapters,
    }


def classes(board: Optional[str] = None) -> list[str]:
    curriculum = curriculum_for_board(board)
    found: set[str] = set()
    for cur in (curriculum, DEFAULT_CURRICULUM):
        for subj_map in cd.CURRICULUM.get(cur, {}).values():
            found.update(subj_map.keys())
    return sorted(found, key=lambda c: int(c) if c.isdigit() else 99)


def subjects_for_class(klass: str, board: Optional[str] = None) -> list[str]:
    return [s for s in config.SUBJECTS if get_syllabus(klass, s, board)]


# Backwards-compatible alias used by some callers.
def subjects_for(klass: str, board: Optional[str] = None) -> list[str]:
    return subjects_for_class(klass, board)


def topics_for(klass: str, subject: str, board: Optional[str] = None) -> list[dict[str, Any]]:
    """Flat list of topics with chapter context."""
    syl = get_syllabus(klass, subject, board)
    if not syl:
        return []
    out = []
    for chapter in syl.get("chapters", []):
        for topic in chapter.get("topics", []):
            out.append(
                {
                    "chapter_id": chapter.get("chapter_id"),
                    "chapter_title": chapter.get("title"),
                    "topic_id": topic.get("topic_id"),
                    "title": topic.get("title"),
                    "skills": topic.get("skills", []),
                    "difficulty_range": topic.get("difficulty_range", [1, 5]),
                }
            )
    return out


def find_topic(klass: str, subject: str, topic_id: Optional[str], board: Optional[str] = None) -> Optional[dict[str, Any]]:
    topics = topics_for(klass, subject, board)
    if not topics:
        return None
    if topic_id:
        for t in topics:
            if t["topic_id"] == topic_id or t["title"].lower() == topic_id.lower():
                return t
    return topics[0]


def all_syllabi(board: Optional[str] = None) -> list[dict[str, Any]]:
    """Every (class, subject) syllabus for a board — used by the admin panel."""
    out = []
    for klass in classes(board):
        for subject in config.SUBJECTS:
            syl = get_syllabus(klass, subject, board)
            if syl:
                out.append(syl)
    return out


def save_syllabus(syl: dict[str, Any], board: Optional[str] = None) -> None:
    """Persist a custom syllabus as a board-specific override file."""
    board = normalize_board(board or syl.get("board"))
    klass = syl.get("class", "x")
    subject = (normalize_subject(syl.get("subject")) or "subject").lower()
    path = config.SYLLABUS_DIR / f"{board}_class{klass}_{subject}.json"
    path.write_text(json.dumps(syl, indent=2, ensure_ascii=False), encoding="utf-8")
