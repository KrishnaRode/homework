"""PrepWell FastAPI app — local-first AI learning agent.

Two-service architecture: this backend owns Ollama, storage, and the adaptive engine;
the Next.js frontend talks to it. No cloud, no telemetry, no external APIs.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .admin.router import router as admin_router
from .auth.router import router as auth_router
from .games.router import router as games_router
from .me_router import router as me_router
from .ollama_client import client as ollama
from .session.router import router as session_router
from .storage import seed
from .syllabus.router import router as syllabus_router

app = FastAPI(title="PrepWell — Learning Agent", version="1.0.0")

# Local-only: allow the Next.js dev origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    seed.run()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "prepwell-backend"}


@app.get("/api/ollama")
def ollama_status() -> dict:
    running = ollama.is_running()
    return {
        "running": running,
        "model": config.MODEL,
        "installed_models": ollama.installed_models() if running else [],
        "message": None if running else "PrepWell needs Ollama running locally. Start it using: ollama serve",
    }


app.include_router(auth_router)
app.include_router(syllabus_router)
app.include_router(session_router)
app.include_router(me_router)
app.include_router(games_router)
app.include_router(admin_router)
