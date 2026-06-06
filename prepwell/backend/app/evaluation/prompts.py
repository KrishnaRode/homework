# =============================================================================
#  File:        backend/app/evaluation/prompts.py
#  Description: Prompt builders for LLM-graded subjective answers.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Rubric prompt for grading subjective answers. Strict JSON output."""
from __future__ import annotations

from typing import Any


def build_eval_prompt(question: dict[str, Any], answer: str) -> str:
    return f"""You are a kind Class {question.get('class')} tutor grading a student's answer.

Question ({question.get('subject')} / {question.get('topic')}):
{question.get('question')}

Expected answer / key idea: {question.get('expected_answer')}
Student's answer: {answer or '(blank)'}

Grade fairly and encouragingly. A partially correct answer earns partial marks.
Never be harsh. Explain how to think about it so the student improves.

Return ONLY this JSON object:
{{
  "correct": true,
  "score": 0,
  "what_was_right": "specific praise for what the student got right",
  "what_was_wrong": "what was missing or incorrect, kindly stated",
  "step_by_step": ["short step", "short step"],
  "how_to_think": "the reasoning strategy to use next time",
  "misconception": "the underlying misunderstanding, or null if none",
  "encouragement": "one warm, motivating sentence"
}}
Set "correct" true only when score >= 60. "score" is 0-100."""
