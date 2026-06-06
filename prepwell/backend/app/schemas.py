# =============================================================================
#  File:        backend/app/schemas.py
#  Description: Pydantic models shared across the API (Question, Evaluation, etc.).
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Pydantic schemas shared across the API."""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ---- Auth ----
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: Literal["student", "admin"]
    student_id: Optional[str] = None
    name: Optional[str] = None
    klass: Optional[str] = None
    board: Optional[str] = None


# ---- Questions ----
class Question(BaseModel):
    question_id: str
    question_hash: str
    klass: str = Field(alias="class")
    subject: str
    topic: str
    difficulty: int = 3
    type: str = "mcq"
    question: str
    options: list[str] = []
    expected_answer: str = ""
    explanation: str = ""
    how_to_think: str = ""
    common_mistake: str = ""
    skill_tags: list[str] = []
    estimated_time_seconds: int = 60
    # Reading-comprehension sets: a shared passage and the question's place in the set.
    passage: str = ""
    passage_id: str = ""
    set_index: int = 0
    set_total: int = 0

    model_config = {"populate_by_name": True}

    def public(self) -> dict[str, Any]:
        """What the student sees BEFORE answering (no answer leakage)."""
        return {
            "question_id": self.question_id,
            "class": self.klass,
            "subject": self.subject,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "type": self.type,
            "question": self.question,
            "options": self.options,
            "skill_tags": self.skill_tags,
            "estimated_time_seconds": self.estimated_time_seconds,
        }


# ---- Session ----
class StartSessionRequest(BaseModel):
    subject: str
    topic: Optional[str] = None  # None => adaptive across subject
    adaptive: bool = False


class StartSessionResponse(BaseModel):
    session_id: str
    subject: str
    topic: Optional[str]
    adaptive: bool


class NextQuestionRequest(BaseModel):
    session_id: str


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str
    time_taken_seconds: int = 0
    used_hint: bool = False


class Evaluation(BaseModel):
    correct: bool
    score: int = 0
    what_was_right: str = ""
    what_was_wrong: str = ""
    step_by_step: list[str] = []
    how_to_think: str = ""
    misconception: Optional[str] = None
    encouragement: str = ""
    expected_answer: str = ""
    next_difficulty: int = 3
    next_type: str = "mcq"


class SessionSummary(BaseModel):
    session_id: str
    total_questions: int
    correct: int
    accuracy: float
    avg_score: float
    strengths: list[str]
    weak_areas: list[str]
    recommended_next_topics: list[str]


# ---- Admin ----
class CreateStudentRequest(BaseModel):
    name: str
    klass: str = Field(alias="class")
    board: str = "cbse"
    username: Optional[str] = None
    password: Optional[str] = None
    model_config = {"populate_by_name": True}


class UpdateStudentRequest(BaseModel):
    name: Optional[str] = None
    klass: Optional[str] = Field(default=None, alias="class")
    board: Optional[str] = None
    password: Optional[str] = None
    model_config = {"populate_by_name": True}


# ---- Brain Games ----
class GameResultRequest(BaseModel):
    game: str
    score: int = 0          # 0-100
    won: bool = False
    duration_seconds: int = 0
