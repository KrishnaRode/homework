# =============================================================================
#  File:        backend/app/games/router.py
#  Description: Brain-games catalog API (warm-up puzzles, never academically scored).
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Brain Games API — a standalone reasoning-games track.

Games are generated and played entirely client-side (local-first, no LLM, no network).
The backend only persists a separate "brain" score so it never affects the academic
mental-model indices.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..auth.deps import require_student
from ..mental_model import service as mm
from ..schemas import GameResultRequest

router = APIRouter(prefix="/api/games", tags=["games"])

# Catalogue of available client-side games (id -> display metadata).
CATALOG = [
    {"id": "memory_grid", "name": "Memory Grid", "skill": "Working memory",
     "blurb": "Memorise the lit tiles, then tap them back."},
    {"id": "odd_one_out", "name": "Odd One Out", "skill": "Visual discrimination",
     "blurb": "Spot the shape that doesn't belong."},
    {"id": "pattern_next", "name": "What Comes Next", "skill": "Sequential reasoning",
     "blurb": "Find the next shape in the pattern."},
    {"id": "count_shapes", "name": "Count the Shapes", "skill": "Visual counting",
     "blurb": "Count how many of one shape are hidden in the mix."},
    {"id": "find_match", "name": "Find the Twin", "skill": "Matching",
     "blurb": "Find the one shape that exactly matches the target."},
]


@router.get("/catalog")
def catalog() -> dict[str, Any]:
    return {"games": CATALOG}


@router.get("/score")
def score(user: dict = Depends(require_student)) -> dict[str, Any]:
    return {"brain": mm.brain_stats(user["student_id"])}


@router.post("/result")
def result(req: GameResultRequest, user: dict = Depends(require_student)) -> dict[str, Any]:
    brain = mm.record_game_result(
        user["student_id"],
        game=req.game,
        score=req.score,
        won=req.won,
        duration_seconds=req.duration_seconds,
    )
    return {"brain": brain}
