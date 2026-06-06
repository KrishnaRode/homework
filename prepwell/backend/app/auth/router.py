# =============================================================================
#  File:        backend/app/auth/router.py
#  Description: Authentication API: login and session token issuance.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Auth routes: login for students and admin."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..schemas import LoginRequest, LoginResponse
from ..storage import db
from . import security

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> LoginResponse:
    user = db.get_user(req.username)
    if not user or not security.verify_password(req.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    role = user["role"]
    student_id = user.get("student_id")
    token = security.make_token({"role": role, "student_id": student_id, "username": req.username})

    name = klass = board = None
    if role == "student" and student_id:
        student = db.get_student(student_id)
        if student:
            name, klass, board = student["name"], student["class"], student.get("board", "cbse")
    return LoginResponse(token=token, role=role, student_id=student_id, name=name, klass=klass, board=board)
