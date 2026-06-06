# PrepWell — Learning Agent

**Prepare smarter. Learn deeper.**

A private, local-first AI tutor that runs entirely on your laptop. PrepWell generates
unlimited *personalized* practice across **Maths, Science, and English**, building a
"mental model" of each student and adapting every question to how they actually perform.

> Free local AI · No cloud · No accounts to the internet · No data leaves your device.
> Part of the **Free AI. Real Problems. Every Sunday.** series.

---

## Why PrepWell

School, coaching, and online platforms are one-size-fits-all. PrepWell adds the missing
layer: it tracks how *this* student does on *every* answer, then chooses the next
question — the right topic, type, and difficulty. It teaches *how to think*, not just
what the answer is.

---

## Architecture

```
Next.js frontend (:3000)  ──HTTP──▶  FastAPI backend (:8000)  ──▶  Ollama (:11434)
                                          │
                                          ├─ SQLite  (auth, students, sessions, history)
                                          └─ JSON     (per-student mental models, syllabus, cache)
```

The **adaptive loop** is the heart:

```
pick subject/topic ─▶ generate question ─▶ student answers ─▶ evaluate
       ▲                                                          │
       └────────── update mental model · choose next ◀───────────┘
```

- **Question engine** (`backend/app/question_engine`) — builds a prompt from the syllabus
  topic + the student's mental model, calls Ollama (strict JSON), validates, de-duplicates
  by `question_hash`, and rotates through 12 question types (never MCQ-only).
- **Evaluation engine** (`backend/app/evaluation`) — deterministic checks for objective
  answers, an LLM rubric for subjective ones; scores 0–100 and explains how to think.
- **Mental model** (`backend/app/mental_model`) — accuracy / speed / confidence / reasoning
  indices + per-topic mastery; decides the next difficulty and what to practice next.
- **Guardrails** (`backend/app/guardrails`) — child-safety filtering, grade-appropriate
  language, JSON repair, and quality regeneration.

---

## Prerequisites

- **Node.js 18.18+** — <https://nodejs.org>
- **Python 3.11–3.13** (avoid 3.14 for now — some wheels aren't published yet)
- **Ollama** — <https://ollama.com/download>

---

## Quick start (one command)

```bash
cd prepwell
./run.sh          # macOS / Linux
# or
run.bat           # Windows
```

`run.sh` starts Ollama, pulls the model (`llama3.2:3b` by default), creates the backend
virtualenv, installs all dependencies, launches the backend on **:8000** and the frontend
on **:3000**, then opens at <http://localhost:3000>.

### Manual start

```bash
# Backend
cd prepwell/backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --app-dir . --port 8000

# Frontend (new terminal)
cd prepwell/frontend
npm install
npm run dev
```

---

## Demo logins

| Role    | Username | Password      |
| ------- | -------- | ------------- |
| Student | `aarav`  | `aarav123`    |
| Student | `diya`   | `diya123`     |
| Admin   | `admin`  | `prepwell123` |

Admins create students and generate their credentials (shown once). Students can only log
in with admin-created accounts.

---

## Seed data

- **Syllabus:** Classes **1–10** Maths, Science, English, curated from the NCERT
  framework in `backend/app/syllabus/curriculum_data.py`
  (normalized: board → class → subject → chapters → topics → skills + difficulty range).
- **Boards:** CBSE, ICSE/CISCE, NIOS, and all major **state boards** (31 total) are
  registered in `curriculum_data.BOARDS`. Each board maps to a curriculum; boards that
  follow NCERT (the large majority) share the base, and any board can be specialised by
  dropping a `data/syllabus/<board>_class<N>_<subject>.json` override file — no code change.
  Resolution falls back gracefully (board → its curriculum → NCERT), so a student never
  hits a missing-syllabus dead end.
- **Students:** `stu_001` (Aarav, CBSE) and `stu_002` (Diya, CBSE) with mental models in
  `data/students/`. Admins pick the board when creating a student.
- The SQLite DB (`data/prepwell.db`) is seeded automatically on first backend start.

---

## Configuration

Backend env (`backend/.env`, see `.env.example`):

| Variable                   | Default                  | Purpose                          |
| -------------------------- | ------------------------ | -------------------------------- |
| `PREPWELL_MODEL`           | `llama3.2:3b`            | Ollama model used for everything |
| `OLLAMA_HOST`              | `http://localhost:11434` | Local Ollama URL                 |
| `MAX_QUESTIONS_PER_SESSION`| `500`                    | Session cap                      |
| `PREPWELL_SECRET`          | (change locally)         | Token signing secret             |
| `PREPWELL_ADMIN_PASSWORD`  | `prepwell123`            | Seeded admin password            |

Frontend env (`frontend/.env.local`): `NEXT_PUBLIC_API_BASE=http://localhost:8000`.

Swap the model with any installed Ollama model, e.g. `PREPWELL_MODEL=qwen2.5-coder ./run.sh`.

---

## Extending

- **More classes/subjects:** drop a normalized JSON into `data/syllabus/` — no code change.
- **Scraping:** `backend/app/syllabus/scraper.py` is a ready extension point; PrepWell never
  depends on live scraping to run.
- **New question types:** add to `config.QUESTION_TYPES` + a hint in
  `question_engine/prompts.py`.

---

## Privacy

PrepWell is local-only: no cloud calls, no telemetry, no external APIs. All student data
(mental models, history, reports) stays in `prepwell/data/` on your machine.

---

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| "PrepWell needs Ollama running" | `ollama serve`, then retry |
| Model not found | `ollama pull llama3.2:3b` |
| `pydantic-core` build fails | Use Python 3.11–3.13, not 3.14 |
| Port in use | `PREPWELL_PORT=8001 ./run.sh` (backend) / `npm run dev -- -p 3001` |
| Frontend can't reach backend | Confirm backend on :8000 and `NEXT_PUBLIC_API_BASE` |
