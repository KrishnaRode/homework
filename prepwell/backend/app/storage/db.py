"""SQLite storage for auth, students, sessions, and asked-question index.

Mental models and full question objects live as JSON files (see files.py); SQLite
holds the relational/index data that benefits from queries.
"""
from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Iterator, Optional

from .. import config

_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


@contextmanager
def cursor() -> Iterator[sqlite3.Cursor]:
    with _lock:
        conn = _connect()
        try:
            cur = conn.cursor()
            yield cur
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    with cursor() as cur:
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                student_id TEXT
            );
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                board TEXT NOT NULL DEFAULT 'cbse',
                username TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT,
                adaptive INTEGER NOT NULL DEFAULT 0,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                total INTEGER NOT NULL DEFAULT 0,
                correct INTEGER NOT NULL DEFAULT 0,
                score_sum INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS asked (
                student_id TEXT NOT NULL,
                question_hash TEXT NOT NULL,
                question_id TEXT NOT NULL,
                session_id TEXT,
                subject TEXT,
                topic TEXT,
                difficulty INTEGER,
                type TEXT,
                correct INTEGER,
                score INTEGER,
                asked_at TEXT NOT NULL,
                PRIMARY KEY (student_id, question_hash)
            );
            """
        )
        # Lightweight migration: add `board` to pre-existing student tables.
        cols = {r["name"] for r in cur.execute("PRAGMA table_info(students)").fetchall()}
        if "board" not in cols:
            cur.execute("ALTER TABLE students ADD COLUMN board TEXT NOT NULL DEFAULT 'cbse'")


# ---- users ----
def add_user(username: str, password_hash: str, role: str, student_id: Optional[str] = None) -> None:
    with cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO users (username, password_hash, role, student_id) VALUES (?,?,?,?)",
            (username, password_hash, role, student_id),
        )


def get_user(username: str) -> Optional[dict[str, Any]]:
    with cursor() as cur:
        row = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None


def user_exists_with_role(role: str) -> bool:
    with cursor() as cur:
        row = cur.execute("SELECT 1 FROM users WHERE role=? LIMIT 1", (role,)).fetchone()
        return row is not None


# ---- students ----
def add_student(student_id: str, name: str, klass: str, username: str, created_at: str, board: str = "cbse") -> None:
    with cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO students (student_id, name, class, board, username, created_at) VALUES (?,?,?,?,?,?)",
            (student_id, name, klass, board, username, created_at),
        )


def list_students() -> list[dict[str, Any]]:
    with cursor() as cur:
        rows = cur.execute("SELECT * FROM students ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_student(student_id: str) -> Optional[dict[str, Any]]:
    with cursor() as cur:
        row = cur.execute("SELECT * FROM students WHERE student_id=?", (student_id,)).fetchone()
        return dict(row) if row else None


def update_student(student_id: str, name: Optional[str], klass: Optional[str], board: Optional[str] = None) -> None:
    with cursor() as cur:
        if name is not None:
            cur.execute("UPDATE students SET name=? WHERE student_id=?", (name, student_id))
        if klass is not None:
            cur.execute("UPDATE students SET class=? WHERE student_id=?", (klass, student_id))
        if board is not None:
            cur.execute("UPDATE students SET board=? WHERE student_id=?", (board, student_id))


def delete_student(student_id: str) -> None:
    with cursor() as cur:
        row = cur.execute("SELECT username FROM students WHERE student_id=?", (student_id,)).fetchone()
        if row and row["username"]:
            cur.execute("DELETE FROM users WHERE username=?", (row["username"],))
        cur.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM sessions WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM asked WHERE student_id=?", (student_id,))


# ---- sessions ----
def create_session(session_id: str, student_id: str, subject: str, topic: Optional[str], adaptive: bool, started_at: str) -> None:
    with cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (session_id, student_id, subject, topic, adaptive, started_at) VALUES (?,?,?,?,?,?)",
            (session_id, student_id, subject, topic, 1 if adaptive else 0, started_at),
        )


def get_session(session_id: str) -> Optional[dict[str, Any]]:
    with cursor() as cur:
        row = cur.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None


def record_answer_in_session(session_id: str, correct: bool, score: int) -> None:
    with cursor() as cur:
        cur.execute(
            "UPDATE sessions SET total=total+1, correct=correct+?, score_sum=score_sum+? WHERE session_id=?",
            (1 if correct else 0, score, session_id),
        )


def end_session(session_id: str, ended_at: str) -> None:
    with cursor() as cur:
        cur.execute("UPDATE sessions SET ended_at=? WHERE session_id=?", (ended_at, session_id))


def recent_sessions(student_id: str, limit: int = 10) -> list[dict[str, Any]]:
    with cursor() as cur:
        rows = cur.execute(
            "SELECT * FROM sessions WHERE student_id=? ORDER BY started_at DESC LIMIT ?",
            (student_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


# ---- asked questions ----
def record_asked(student_id: str, question_hash: str, question_id: str, session_id: str,
                 subject: str, topic: str, difficulty: int, qtype: str, asked_at: str) -> None:
    with cursor() as cur:
        cur.execute(
            """INSERT OR IGNORE INTO asked
               (student_id, question_hash, question_id, session_id, subject, topic, difficulty, type, asked_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (student_id, question_hash, question_id, session_id, subject, topic, difficulty, qtype, asked_at),
        )


def mark_asked_result(student_id: str, question_id: str, correct: bool, score: int) -> None:
    with cursor() as cur:
        cur.execute(
            "UPDATE asked SET correct=?, score=? WHERE student_id=? AND question_id=?",
            (1 if correct else 0, score, student_id, question_id),
        )


def asked_hashes(student_id: str) -> set[str]:
    with cursor() as cur:
        rows = cur.execute("SELECT question_hash FROM asked WHERE student_id=?", (student_id,)).fetchall()
        return {r["question_hash"] for r in rows}


def question_history(student_id: str, limit: int = 100) -> list[dict[str, Any]]:
    with cursor() as cur:
        rows = cur.execute(
            "SELECT * FROM asked WHERE student_id=? ORDER BY asked_at DESC LIMIT ?",
            (student_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def reset_student_history(student_id: str) -> None:
    with cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE student_id=?", (student_id,))
        cur.execute("DELETE FROM asked WHERE student_id=?", (student_id,))
