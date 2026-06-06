"""Student self-service: own progress + own report (no admin needed)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from .auth.deps import require_student
from .mental_model import service as mm
from .reports import service as reports
from .storage import db

router = APIRouter(prefix="/api/me", tags=["me"])


@router.get("/progress")
def my_progress(user: dict = Depends(require_student)) -> dict[str, Any]:
    sid = user["student_id"]
    return {"summary": mm.summary(sid), "recent_sessions": db.recent_sessions(sid)}


@router.get("/report")
def my_report(format: str = "json", user: dict = Depends(require_student)):
    data = reports.build_report(user["student_id"])
    if format == "html":
        return HTMLResponse(reports.render_html(data))
    return JSONResponse(data)
