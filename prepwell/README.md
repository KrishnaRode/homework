# PrepWell — Learning Agent

**Prepare smarter. Learn deeper.**

A private, **local-first AI tutor** that runs entirely on your laptop. PrepWell generates
unlimited *personalized* practice across **Maths, Science, and English**, builds a
"mental model" of each student, and adapts every question to how they actually perform —
all without sending a single byte to the cloud.

<p>
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg" />
  <img alt="Backend: FastAPI" src="https://img.shields.io/badge/Backend-FastAPI-009688.svg" />
  <img alt="Frontend: Next.js 15" src="https://img.shields.io/badge/Frontend-Next.js%2015-000000.svg" />
  <img alt="LLM: Ollama (local)" src="https://img.shields.io/badge/LLM-Ollama%20(local)-7c3aed.svg" />
  <img alt="Privacy: 100%25 local" src="https://img.shields.io/badge/Privacy-100%25%20local-16a34a.svg" />
</p>

> Free local AI · No cloud · No internet accounts · No data leaves your device.
> Part of the **Free AI. Real Problems. Every Sunday.** series.

---

## Table of contents

- [Why PrepWell](#why-prepwell)
- [Features](#features)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [System requirements](#system-requirements)
- [Quick start](#quick-start-one-command)
- [Manual setup](#manual-setup)
- [Demo logins](#demo-logins)
- [Configuration](#configuration)
- [Project structure](#project-structure)
- [API overview](#api-overview)
- [Seed data & syllabus](#seed-data--syllabus)
- [Testing](#testing)
- [Extending](#extending)
- [Privacy](#privacy)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Author](#author)

---

## Why PrepWell

School, coaching, and online platforms are one-size-fits-all. PrepWell adds the missing
layer: it tracks how *this* student does on *every* answer, then chooses the next
question — the right topic, type, and difficulty. It teaches *how to think*, not just
what the answer is. Because it runs on a local LLM (via Ollama), there are no API bills,
no rate limits, and no privacy trade-offs.

---

## Features

- 🎯 **Adaptive questions** — every question is generated for the student: right topic,
  type, and difficulty, based on live performance.
- 🧠 **Mental model per student** — tracks accuracy, speed, confidence, and reasoning,
  then plans what to practice next.
- 💡 **Teaches how to think** — every answer explains the strategy and the common mistake,
  never just right/wrong.
- 📖 **12 question types** — MCQ, short answer, explain, fill-in-the-blank, true/false +
  reason, step problems, word problems, reading comprehension (passage + question set),
  spot-the-mistake, and more.
- 🎮 **Brain games while you wait** — optional, non-academic warm-up puzzles shown during
  question generation (never scored, never touch learning indices).
- 👨‍🏫 **Admin console** — admins create students and issue one-time credentials.
- 🔒 **100% local & private** — runs on free local AI; no cloud, no telemetry.

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

## Tech stack

| Layer        | Technology                                                        |
| ------------ | ----------------------------------------------------------------- |
| Frontend     | Next.js 15 (App Router), React 19, TypeScript 5, Tailwind CSS v4  |
| Backend      | Python 3.11–3.13, FastAPI, Pydantic v2, Uvicorn                   |
| Local LLM    | Ollama running `llama3.2:3b` (swappable)                          |
| Storage      | SQLite (relational state) + JSON files (mental models, cache)     |
| Tooling      | `run.sh` one-command launcher; npm; venv                          |

---

## System requirements

PrepWell runs a real large language model **locally**, so the main resource cost is RAM and
disk for the model — not a network connection.

**Software**

- **Node.js 18.18+** — <https://nodejs.org>
- **Python 3.11–3.13** (avoid 3.14 for now — some wheels aren't published yet)
- **Ollama** — <https://ollama.com/download>
- **OS** — macOS, Linux, or Windows (WSL2 recommended on Windows)

**Hardware** (driven by the local LLM)

| Resource | Minimum                       | Recommended                          |
| -------- | ----------------------------- | ------------------------------------ |
| RAM      | 8 GB                          | 16 GB+ (smoother with other apps open) |
| Disk     | ~5 GB free                    | 10 GB+ (model ≈ 2 GB + deps + data)  |
| CPU      | Any modern 64-bit multi-core  | Apple Silicon / recent x86           |
| GPU      | Not required (CPU inference)  | Any Ollama-supported GPU = faster    |

> **Note on speed:** with the default `llama3.2:3b` on CPU-only machines, the **first
> question** of a session typically takes ~10–25s to generate; later questions are
> prefetched in the background and usually appear instantly. A GPU (or Apple Silicon)
> reduces this significantly. The UI always shows an honest "Preparing your question…"
> status while this happens.

---

## Quick start (one command)

```bash
cd prepwell
./run.sh          # macOS / Linux
```

`run.sh` checks prerequisites, starts Ollama, pulls the model (`llama3.2:3b` by default),
creates the backend virtualenv, installs all dependencies, launches the backend on
**:8000** and the frontend on **:3000**, then serves the app at <http://localhost:3000>.

---

## Manual setup

```bash
# 0) Start Ollama and pull the model (first run only)
ollama serve &
ollama pull llama3.2:3b

# 1) Backend
cd prepwell/backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --app-dir . --port 8000

# 2) Frontend (new terminal)
cd prepwell/frontend
npm install
npm run dev
```

Then open <http://localhost:3000>.

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

## Configuration

Backend env (`backend/.env`, see `backend/.env.example`):

| Variable                    | Default                  | Purpose                          |
| --------------------------- | ------------------------ | -------------------------------- |
| `PREPWELL_MODEL`            | `llama3.2:3b`            | Ollama model used for everything |
| `OLLAMA_HOST`               | `http://localhost:11434` | Local Ollama URL                 |
| `MAX_QUESTIONS_PER_SESSION` | `500`                    | Session cap                      |
| `PREPWELL_SECRET`           | (change locally)         | Token signing secret             |
| `PREPWELL_ADMIN_PASSWORD`   | `prepwell123`            | Seeded admin password            |
| `PREPWELL_PORT`             | `8000`                   | Backend port                     |

Frontend env (`frontend/.env.local`): `NEXT_PUBLIC_API_BASE=http://localhost:8000`.

Swap the model with any installed Ollama model, e.g. `PREPWELL_MODEL=qwen2.5 ./run.sh`.

---

## Project structure

```
prepwell/
├── backend/                     # FastAPI service (the adaptive engine)
│   └── app/
│       ├── main.py              # app factory, CORS, health, route wiring
│       ├── config.py            # model, ports, secrets, question types
│       ├── schemas.py           # Pydantic models (Question, Evaluation, …)
│       ├── question_engine/     # prompt → Ollama → validate → de-duplicate
│       ├── evaluation/          # deterministic + LLM rubric grading
│       ├── mental_model/        # per-student indices + next-step planning
│       ├── guardrails/          # child-safety, grade-appropriate, JSON repair
│       ├── session/             # start / next / answer / stop
│       ├── syllabus/            # curriculum data, boards, resolution
│       ├── ollama_client/       # thin local Ollama HTTP client
│       ├── storage/             # SQLite (db.py) + JSON files (files.py) + seed
│       ├── auth/                # login, tokens, dependencies
│       ├── admin/               # roster + credential management
│       └── games/               # brain-game catalog
├── frontend/                    # Next.js App Router UI
│   ├── app/                     # routes: /, /login, /dashboard, /session, /report, /admin, /games
│   ├── components/              # Brand, Footer, QuestionCard, AnswerView, LoadingState, games/
│   └── lib/                     # api, auth, types, brainGames
├── data/                        # local-only runtime data (students, cache)
├── run.sh                       # one-command launcher
├── LICENSE                      # MIT
└── README.md
```

---

## API overview

All endpoints are served by the backend at `http://localhost:8000`.

| Method | Endpoint              | Purpose                                   |
| ------ | --------------------- | ----------------------------------------- |
| GET    | `/api/health`         | Service health check                      |
| GET    | `/api/ollama`         | Ollama status + installed models          |
| POST   | `/api/auth/login`     | Log in (student or admin)                 |
| GET    | `/api/syllabus/...`   | Boards, classes, subjects, chapters       |
| POST   | `/api/session/start`  | Start a practice session                  |
| POST   | `/api/session/next`   | Get the next adaptive question            |
| POST   | `/api/session/answer` | Submit an answer, get evaluation          |
| POST   | `/api/session/stop`   | End session, get summary                  |
| GET    | `/api/me/...`         | Current user profile + mental model       |
| GET    | `/api/games/...`      | Brain-game catalog                        |
| POST   | `/api/admin/...`      | Create students, issue credentials        |

Interactive API docs are available at <http://localhost:8000/docs> while the backend runs.

---

## Seed data & syllabus

- **Syllabus:** Classes **1–10** Maths, Science, English, curated from the NCERT
  framework in `backend/app/syllabus/curriculum_data.py`
  (normalized: board → class → subject → chapters → topics → skills + difficulty range).
- **Boards:** CBSE, ICSE/CISCE, NIOS, and all major **state boards** (31 total) are
  registered in `curriculum_data.BOARDS`. Boards that follow NCERT share the base, and any
  board can be specialised by dropping a `data/syllabus/<board>_class<N>_<subject>.json`
  override — no code change. Resolution falls back gracefully (board → curriculum → NCERT).
- **Students:** `stu_001` (Aarav, CBSE) and `stu_002` (Diya, CBSE) ship with mental models
  in `data/students/`. Admins pick the board when creating a student.
- The SQLite DB (`data/prepwell.db`) is seeded automatically on first backend start.

---

## Testing

With both servers running, a quick end-to-end smoke check:

```bash
curl -s http://localhost:8000/api/health     # -> {"status":"ok","service":"prepwell-backend"}
curl -s http://localhost:8000/api/ollama      # -> Ollama status + installed models
```

Then open <http://localhost:3000>, log in with a demo account, and start a session to
confirm questions generate and grade end-to-end.

---

## Extending

- **More classes/subjects:** drop a normalized JSON into `data/syllabus/` — no code change.
- **Scraping:** `backend/app/syllabus/scraper.py` is a ready extension point; PrepWell never
  depends on live scraping to run.
- **New question types:** add to `config.QUESTION_TYPES` + a hint in
  `question_engine/prompts.py`.
- **New brain games:** add a generator in `frontend/lib/brainGames.ts` and a component in
  `frontend/components/games/`.

---

## Privacy

PrepWell is local-only: no cloud calls, no telemetry, no external APIs at runtime. All
student data (mental models, history, reports) stays in `prepwell/data/` on your machine.

---

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| "PrepWell needs Ollama running" | `ollama serve`, then retry |
| Model not found | `ollama pull llama3.2:3b` |
| First question is slow | Normal on CPU-only machines (~10–25s); later questions prefetch. Use a smaller model or a GPU to speed up. |
| `pydantic-core` build fails | Use Python 3.11–3.13, not 3.14 |
| Port in use | `PREPWELL_PORT=8001 ./run.sh` (backend) / `npm run dev -- -p 3001` |
| Frontend can't reach backend | Confirm backend on :8000 and `NEXT_PUBLIC_API_BASE` |
| Out of memory | Close other apps, or use a smaller model (e.g. `llama3.2:1b`) |

---

## License

Released under the **MIT License** — see [LICENSE](./LICENSE). Copyright © 2026 Krishna Rode.

---

## Author

**Developed by Krishna Rode.**
Part of the *Free AI. Real Problems. Every Sunday.* series.
