# PrepWell — Full Build Brief (authoritative)

> This is the verbatim product brief PrepWell is built from. `project.md` (repo root) is
> the contract; this file is the detailed source of truth for architecture and features.
> Decisions locked with the owner: **full platform**, **Next.js + FastAPI**, default model
> **`llama3.2:3b`** (installed locally).

Build a complete local-first AI learning product named **PrepWell**.

## Goal
PrepWell helps school students prepare topics across subjects like English, Maths, and
Science using free local AI. It runs on a normal laptop using a free stack: Next.js
frontend, FastAPI backend, Ollama local LLM, local JSON/SQLite storage, no cloud, no API
keys, no subscriptions.

## Core idea
PrepWell is a learning agent that generates unlimited personalized practice questions
based on: (1) selected class/standard, (2) selected subject, (3) current syllabus/topics,
(4) student's past performance, (5) student's mental model stored locally. It should feel
like a serious learning engine, not a basic quiz app.

## Tech stack
- Frontend: Next.js + React + TailwindCSS
- Backend: FastAPI
- Local AI: Ollama (default `llama3.2:3b`)
- Storage: local JSON files plus SQLite where useful
- No paid APIs, no cloud dependency, run with one command where possible

## Major features

### 1. Landing + Student Flow
Clean, modern, playful UI. Product name PrepWell, tagline "Prepare smarter. Learn deeper."
Login screen for students (admin-created credentials only). After login the student picks
Class/Standard, Subject, Topic or "Start Adaptive Session". Questions are generated one by
one in real time. Session limit: max 500 questions. Student can stop anytime. At the end:
session summary, strengths, weak areas, next recommended topics.

### 2. Admin Panel
One local admin account. Admin can: add/edit/delete students; generate username/password;
assign class/standard; view progress; view mental-model summary; reset session history;
manage syllabus sources/files; manage subjects/topics; view question history; export
student report as JSON/HTML.

### 3. Syllabus Engine
Store syllabus locally by class, subject, chapter, topic, subtopic. Seed syllabus JSON in
repo for at least Class 5 Maths/Science/English. Scraper-ready architecture but no
dependency on live scraping to run; include a module that can later scrape public syllabus
pages. Normalized structure:
```json
{ "class": "5", "subject": "Maths", "chapters": [
  { "chapter_id": "fractions", "title": "Fractions", "topics": [
    { "topic_id": "adding_fractions", "title": "Adding Fractions",
      "skills": ["same denominator", "different denominator", "simplification"],
      "difficulty_range": [1, 5] } ] } ] }
```

### 4. Student Mental Model
Each student has a local mental model JSON, updated after every answer. Tracks accuracy,
time taken, hint usage, difficulty attempted, mistake type, confidence, topic mastery,
repetition risk, weak concepts, recommended next step. Structure:
```json
{ "student_id": "stu_001", "class": "5", "overall_index": 62, "confidence_index": 55,
  "speed_index": 48, "accuracy_index": 70, "reasoning_index": 50,
  "topic_mastery": { "maths.fractions.adding_fractions": {
    "mastery": 61, "attempts": 14, "correct": 9,
    "wrong_patterns": ["LCM confusion", "simplification missed"],
    "last_seen": "timestamp", "next_difficulty": 3, "repeat_lock": ["question_hash_1"] } },
  "learning_style": { "prefers_visual": true, "needs_step_by_step": true,
    "gets_fast_questions_wrong": false },
  "recent_mistakes": [], "recommended_next_topics": [] }
```

### 5. Question Generation Engine
Generate unique questions from syllabus + mental model. Types: MCQ, short answer, explain
in your own words, fill in the blanks, true/false with reason, diagram-based, step-by-step
problem, real-life word problem, reasoning puzzle, game-like, match the following, spot the
mistake, improve/correct the answer. Each question object includes question_id,
question_hash, class, subject, topic, difficulty, type, question, options, expected_answer,
explanation, how_to_think, common_mistake, skill_tags, estimated_time_seconds. Avoid
repeats per student (question_hash + similarity), maintain per-student asked history, cache
in a local queue, pre-generate next questions in background where possible.

### 6. Answer Evaluation Engine
For every answer: evaluate correctness; score 0–100; explain right/wrong; step-by-step
solution; "how to think"; identify misconception; update mental model; decide next
difficulty + next type. Subjective → Ollama with a strict rubric; objective → deterministic
checking first.

### 7. Adaptive Session Logic
Behave like a tutor: correct+fast → raise difficulty slowly; struggling → lower difficulty
and explain better; repeated mistake → foundational question; bored/slow → game-like
question; performing well → challenge mode. Mix question types; do not ask only MCQs.

### 8. Engagement Games
While generating, show lightweight preloaded brain games (pattern matching, number
sequence, memory cards, shape rotation, quick logic, word scramble, odd-one-out). Built
into frontend, not AI-dependent, short, optional.

### 9. UI/UX
Modern, child-friendly, minimal, fast, responsive, dark/light. Progress bar, optional
mascot, clear question cards, light animations, beautiful answer explanations, "why this
matters", streaks/badges/mastery bars. Pages: landing, login, student dashboard, start
session, active session, result/explanation, progress report, admin dashboard, student
management, syllabus management.

### 10. Guardrails
No harmful/adult/political/inappropriate content; grade-appropriate language; difficulty
matches class; encouraging never insulting; repair invalid JSON; regenerate poor questions;
never expose answer before submit; no cloud calls; no telemetry; no external API; local-only
privacy notice.

### 11. File Structure
`prepwell/{frontend,backend,data{syllabus,students,question_history,generated_cache},games}`
with `backend/app/{main.py,auth,syllabus,mental_model,question_engine,evaluation,session,admin,ollama_client,guardrails}`, README, optional docker-compose, start scripts.

### 12. Ollama Integration
Configurable model (default `llama3.2:3b`). Check Ollama is running; if not, show:
"PrepWell needs Ollama running locally. Start it using: ollama serve".

### 13. Prompting
Strong internal prompts for question generation, answer evaluation, explanation, mental
model update suggestions, syllabus topic expansion, question quality review. All LLM output
requested as strict JSON.

### 14. Reports
Overall learning index, subject-wise score, topic mastery, weak areas, strengths, mistake
patterns, recommended next practice, recent sessions, parent-friendly summary, export HTML
+ JSON.

### 15. Quality
Thoughtful, varied, useful questions. Explanations teach *how to think*. Adaptive engine +
mental model are the heart.

### 16. Deliverables
Full working codebase: README, sample students, sample syllabus, sample questions, local
run commands, architecture notes, demo admin credentials, seed data, clean UI.

### 17. Tone
"A private AI tutor on your laptop that understands how every student learns."
Production-quality local MVP, cleanly structured, easy to extend.
