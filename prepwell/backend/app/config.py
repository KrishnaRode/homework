# =============================================================================
#  File:        backend/app/config.py
#  Description: Central configuration: model, ports, secrets, question types, limits.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Central configuration. All values overridable via environment (.env)."""
from __future__ import annotations

import os
from pathlib import Path

# Load .env if present (tiny parser, no extra dependency).
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if _ENV_PATH.exists():
    for _line in _ENV_PATH.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _, _v = _line.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip())

# Repo layout: <repo>/prepwell/{backend,data}
BACKEND_DIR = Path(__file__).resolve().parent.parent
PREPWELL_DIR = BACKEND_DIR.parent
DATA_DIR = PREPWELL_DIR / "data"
SYLLABUS_DIR = DATA_DIR / "syllabus"
CURRICULA_DIR = SYLLABUS_DIR / "curricula"
STUDENTS_DIR = DATA_DIR / "students"
HISTORY_DIR = DATA_DIR / "question_history"
CACHE_DIR = DATA_DIR / "generated_cache"
DB_PATH = DATA_DIR / "prepwell.db"

for _d in (DATA_DIR, SYLLABUS_DIR, CURRICULA_DIR, STUDENTS_DIR, HISTORY_DIR, CACHE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Ollama
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
MODEL = os.environ.get("PREPWELL_MODEL", "llama3.2:3b")
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120"))

# Server
HOST = os.environ.get("PREPWELL_HOST", "0.0.0.0")
PORT = int(os.environ.get("PREPWELL_PORT", "8000"))
SECRET = os.environ.get("PREPWELL_SECRET", "change-me-locally-only")

# Session
MAX_QUESTIONS = int(os.environ.get("MAX_QUESTIONS_PER_SESSION", "500"))

# Demo admin
ADMIN_USER = os.environ.get("PREPWELL_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("PREPWELL_ADMIN_PASSWORD", "prepwell123")

# Allowed enums
SUBJECTS = ["Maths", "Science", "English"]
DEFAULT_BOARD = os.environ.get("PREPWELL_DEFAULT_BOARD", "cbse")
QUESTION_TYPES = [
    "mcq", "short_answer", "explain", "fill_blank", "true_false_reason",
    "diagram", "step_problem", "word_problem", "reasoning", "match",
    "spot_mistake", "improve_answer",
]
