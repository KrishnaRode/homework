"""Public syllabus reads (boards, classes, subjects, topics)."""
from __future__ import annotations

from fastapi import APIRouter, Query

from . import service

router = APIRouter(prefix="/api/syllabus", tags=["syllabus"])


@router.get("/boards")
def boards() -> dict:
    return {"boards": service.boards()}


@router.get("/classes")
def classes(board: str = "cbse") -> dict:
    return {"board": service.normalize_board(board), "classes": service.classes(board)}


@router.get("/subjects")
def subjects(klass: str = Query(alias="class"), board: str = "cbse") -> dict:
    return {"class": klass, "board": service.normalize_board(board),
            "subjects": service.subjects_for_class(klass, board)}


@router.get("/topics")
def topics(klass: str = Query(alias="class"), subject: str = Query(...), board: str = "cbse") -> dict:
    return {"class": klass, "subject": subject, "board": service.normalize_board(board),
            "topics": service.topics_for(klass, subject, board)}
