# =============================================================================
#  File:        backend/app/auth/deps.py
#  Description: FastAPI dependencies for resolving and guarding the current user.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""FastAPI auth dependencies."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, Header, HTTPException, status

from . import security


def current_user(authorization: str = Header(default="")) -> dict[str, Any]:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = security.decode_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return payload


def require_admin(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user.get("role") != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


def require_student(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user.get("role") != "student" or not user.get("student_id"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Student access required")
    return user
