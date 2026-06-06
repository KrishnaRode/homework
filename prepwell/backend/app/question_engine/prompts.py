# =============================================================================
#  File:        backend/app/question_engine/prompts.py
#  Description: Prompt builders for adaptive questions and comprehension sets.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Prompt builders for question generation. All outputs requested as strict JSON."""
from __future__ import annotations

from typing import Any

_TYPE_HINTS = {
    "mcq": "a multiple-choice question with exactly 4 options, only one correct",
    "short_answer": "a question answered in one short phrase or number",
    "explain": "ask the student to explain a concept in their own words",
    "fill_blank": "a fill-in-the-blank sentence using ___ for the blank",
    "true_false_reason": "a true/false statement; the student must also give a reason",
    "diagram": "describe a simple diagram in words and ask about it (no image needed)",
    "step_problem": "a problem that requires showing step-by-step working",
    "word_problem": "a real-life word problem the student can relate to",
    "reasoning": "a logic/reasoning puzzle tied to the topic",
    "match": "a match-the-following with 3-4 pairs; put pairs in options as 'A - B'",
    "spot_mistake": "show a worked answer containing one mistake; ask the student to find it",
    "improve_answer": "show a weak answer and ask the student to improve it",
}


def build_generation_prompt(
    *,
    klass: str,
    subject: str,
    topic: dict[str, Any],
    difficulty: int,
    qtype: str,
    wrong_patterns: list[str],
    avoid_questions: list[str],
    board: str = "CBSE",
) -> str:
    skills = ", ".join(topic.get("skills", [])) or topic.get("title", "")
    type_hint = _TYPE_HINTS.get(qtype, _TYPE_HINTS["short_answer"])
    weak = (
        f"This student has previously struggled with: {', '.join(wrong_patterns)}. "
        "Gently target those gaps. "
        if wrong_patterns
        else ""
    )
    avoid = (
        "Do NOT repeat or closely paraphrase any of these recent questions:\n- "
        + "\n- ".join(avoid_questions[:8])
        if avoid_questions
        else ""
    )
    return f"""You are creating ONE practice question for a Class {klass} student following the {board} curriculum.

Subject: {subject}
Topic: {topic.get('title')}
Skills to test: {skills}
Difficulty: {difficulty} on a 1-5 scale (1 = very easy, 5 = challenging) — match it exactly.
Question style: {type_hint}.

{weak}{avoid}

Rules:
- Age- and grade-appropriate, friendly, encouraging.
- The "how_to_think" field must teach the reasoning strategy, not just restate the answer.
- For MCQ, "options" has 4 entries and "expected_answer" must exactly match one option.
- Keep it self-contained (no external images or links required).

Return ONLY this JSON object:
{{
  "type": "{qtype}",
  "difficulty": {difficulty},
  "topic": "{topic.get('title')}",
  "question": "the question text shown to the student",
  "options": ["..."],
  "expected_answer": "the correct answer",
  "explanation": "why this is the answer, in plain language",
  "how_to_think": "the step-by-step thinking strategy a student should use",
  "common_mistake": "the typical mistake students make here",
  "skill_tags": ["..."],
  "estimated_time_seconds": 60
}}"""


def _class_number(klass: str) -> int:
    digits = "".join(ch for ch in str(klass) if ch.isdigit())
    try:
        return int(digits) if digits else 5
    except ValueError:
        return 5


def build_comprehension_prompt(
    *,
    klass: str,
    subject: str,
    topic: dict[str, Any],
    difficulty: int,
    count: int,
    board: str = "CBSE",
    avoid_passages: list[str] | None = None,
) -> str:
    """Prompt for a reading-comprehension SET: one passage + several questions on it."""
    skills = ", ".join(topic.get("skills", [])) or topic.get("title", "")
    cls = _class_number(klass)
    words = 60 if cls <= 3 else 90 if cls <= 5 else 130 if cls <= 8 else 180
    avoid = (
        "Do NOT reuse or closely paraphrase any of these recent passages:\n- "
        + "\n- ".join(p[:120] for p in avoid_passages[:5])
        if avoid_passages
        else ""
    )
    return f"""You are creating a READING COMPREHENSION exercise for a Class {klass} student following the {board} curriculum.

Subject: {subject}
Topic: {topic.get('title')}
Skills to test: {skills}
Difficulty: {difficulty} on a 1-5 scale (1 = very easy, 5 = challenging) — match it exactly.

Write ONE short, original, age-appropriate passage of about {words} words, then {count} questions that can be answered ONLY by reading that passage.

{avoid}

Rules:
- The passage must be self-contained, friendly, and grade-appropriate (no scary, adult, violent, or political themes).
- Vary the question styles: include some multiple-choice (exactly 4 options, one correct) and some short-answer. Cover the main idea, specific details, vocabulary-in-context, and one simple inference.
- Every question must be answerable from the passage ALONE — never require outside knowledge.
- For each MCQ, "options" has exactly 4 entries and "expected_answer" must exactly match one option.
- "how_to_think" must teach the reading strategy (e.g. "scan the passage for the sentence about ...").

Return ONLY this JSON object (exactly {count} items in "questions"):
{{
  "passage": "the reading passage text",
  "questions": [
    {{
      "type": "mcq",
      "question": "the question text shown to the student",
      "options": ["...", "...", "...", "..."],
      "expected_answer": "the correct answer",
      "explanation": "why this is the answer, referring to the passage",
      "how_to_think": "the reading strategy a student should use to find it",
      "common_mistake": "the typical mistake students make here",
      "skill_tags": ["..."],
      "estimated_time_seconds": 45
    }}
  ]
}}"""
