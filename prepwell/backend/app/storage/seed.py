"""Seed the demo admin + sample students on first run. Idempotent."""
from __future__ import annotations

from datetime import datetime, timezone

from .. import config
from ..auth import security
from ..mental_model import service as mm
from . import db, files

# (student_id, name, class, board, username, password) — mental-model JSON already in data/students.
_SAMPLE_STUDENTS = [
    ("stu_001", "Aarav", "5", "cbse", "aarav", "aarav123"),
    ("stu_002", "Diya", "5", "cbse", "diya", "diya123"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run() -> None:
    db.init_db()

    if not db.user_exists_with_role("admin"):
        db.add_user(
            config.ADMIN_USER,
            security.hash_password(config.ADMIN_PASSWORD),
            "admin",
            None,
        )

    for student_id, name, klass, board, username, password in _SAMPLE_STUDENTS:
        if db.get_student(student_id):
            continue
        db.add_user(username, security.hash_password(password), "student", student_id)
        db.add_student(student_id, name, klass, username, _now(), board=board)
        if not files.load_mental_model(student_id):
            files.save_mental_model(student_id, mm.default_model(student_id, name, klass, board))
