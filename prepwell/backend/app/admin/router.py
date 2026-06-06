# =============================================================================
#  File:        backend/app/admin/router.py
#  Description: Admin API: create students, issue credentials, manage roster.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Admin panel API: manage students, view progress, syllabus, export reports."""
from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse

from ..auth.deps import require_admin
from ..auth import security
from ..mental_model import service as mm
from ..reports import service as reports
from ..schemas import CreateStudentRequest, UpdateStudentRequest
from ..storage import db, files
from ..syllabus import service as syllabus

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "", name.lower())[:10] or "student"
    return f"{base}{secrets.randbelow(900) + 100}"


@router.get("/students")
def list_students() -> dict[str, Any]:
    rows = db.list_students()
    for r in rows:
        summ = mm.summary(r["student_id"])
        r["overall_index"] = summ["overall_index"]
    return {"students": rows}


@router.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(req: CreateStudentRequest) -> dict[str, Any]:
    student_id = f"stu_{uuid.uuid4().hex[:8]}"
    username = req.username or _slug(req.name)
    if db.get_user(username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    password = req.password or secrets.token_urlsafe(6)
    board = syllabus.normalize_board(req.board)
    db.add_user(username, security.hash_password(password), "student", student_id)
    db.add_student(student_id, req.name, req.klass, username, _now(), board=board)
    files.save_mental_model(student_id, mm.default_model(student_id, req.name, req.klass, board))
    # Return the generated password ONCE so the admin can share it.
    return {"student_id": student_id, "username": username, "password": password,
            "name": req.name, "class": req.klass, "board": board}


@router.patch("/students/{student_id}")
def update_student(student_id: str, req: UpdateStudentRequest) -> dict[str, Any]:
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    board = syllabus.normalize_board(req.board) if req.board else None
    db.update_student(student_id, req.name, req.klass, board)
    if req.password and student["username"]:
        db.add_user(student["username"], security.hash_password(req.password), "student", student_id)
    return {"ok": True}


@router.delete("/students/{student_id}")
def delete_student(student_id: str) -> dict[str, Any]:
    db.delete_student(student_id)
    path = files.mental_model_path(student_id)
    if path.exists():
        path.unlink()
    return {"ok": True}


@router.post("/students/{student_id}/reset")
def reset_history(student_id: str) -> dict[str, Any]:
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    db.reset_student_history(student_id)
    files.save_mental_model(
        student_id,
        mm.default_model(student_id, student["name"], student["class"], student.get("board", "cbse")),
    )
    log = files.question_log_path(student_id)
    if log.exists():
        log.unlink()
    return {"ok": True}


@router.get("/students/{student_id}/progress")
def progress(student_id: str) -> dict[str, Any]:
    return {"summary": mm.summary(student_id), "recent_sessions": db.recent_sessions(student_id)}


@router.get("/students/{student_id}/history")
def history(student_id: str) -> dict[str, Any]:
    return {"history": db.question_history(student_id, limit=200)}


@router.get("/students/{student_id}/report")
def report(student_id: str, format: str = "json"):
    data = reports.build_report(student_id)
    if format == "html":
        return HTMLResponse(reports.render_html(data))
    return JSONResponse(data)


# ---- boards + syllabus management ----
@router.get("/boards")
def list_boards() -> dict[str, Any]:
    return {"boards": syllabus.boards()}


@router.get("/syllabus")
def list_syllabi(board: str = "cbse") -> dict[str, Any]:
    return {"board": syllabus.normalize_board(board), "syllabi": syllabus.all_syllabi(board)}


@router.put("/syllabus")
def save_syllabus(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    if not payload.get("class") or not payload.get("subject"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "class and subject are required")
    syllabus.save_syllabus(payload)
    return {"ok": True}
