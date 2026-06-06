# Project Definition — PrepWell — Learning Agent

> The spec for this Sunday build. Section 1 mirrors [`app.config.ts`](app.config.ts).
> The full product brief lives in [`PROMPT.md`](PROMPT.md); this file is the contract.
>
> **Note:** PrepWell intentionally goes beyond the single-screen template — it is a
> two-service, local-first learning *platform* (Next.js frontend + FastAPI backend +
> Ollama + SQLite/JSON). The brand, design system, and "the answer teaches" philosophy
> are kept; the "one screen, no backend" constraint is deliberately relaxed.

---

## 1. Identity (placeholders → `app.config.ts`)

| Placeholder            | Value                                                            |
| ---------------------- | --------------------------------------------------------------- |
| `{{PRODUCT_NAME}}`     | PrepWell — Learning Agent                                        |
| `{{TAGLINE}}`          | Prepare smarter. Learn deeper.                                  |
| `{{DESCRIPTION}}`      | Free, local-first AI learning agent that generates unlimited personalized practice (Maths/English/Science) adapting to each student's performance. |
| `{{OLLAMA_MODEL}}`     | `llama3.2:3b` (installed; swap via `PREPWELL_MODEL`)             |
| `{{REPO_URL}}`         | https://github.com/KrishnaRode/homework                         |
| `{{API_ROUTE}}`        | FastAPI base `/api` — core loop: `POST /api/session/next`, `POST /api/session/answer` |
| `{{PRIMARY_INPUT}}`    | A student's class + subject + topic, then their answers in a live session |
| `{{PRIMARY_ACTION}}`   | Practice (Start Adaptive Session)                               |

> The backend owns the Ollama model. `prepwell/backend/.env.example` documents
> `PREPWELL_MODEL` (default `llama3.2:3b`).

---

## 2. The problem this solves

Students today have school teaching, external coaching, and online platforms — but all
of these are one-size-fits-all. There is no layer that captures **personal growth** and
**personalized tracking**: how *this* student performs on *each* action and answer, and
what they should practice next because of it. PrepWell is a real practicer with a
personal touch — a learning agent that builds a private "mental model" of each student
and uses it to generate the next question, at the right difficulty and type. Running
locally and free matters because it keeps a child's learning data private (no cloud, no
telemetry) and removes the subscription barrier for every family.

---

## 3. Input → Output contract

The core is an **adaptive loop**, not a single request. Two backend routes drive it; both
read/write the student's mental model and asked-question history.

- **Input:** student identity + selected `class`, `subject`, `topic` (or "Adaptive
  Session"). Then, per turn, the student's submitted answer.
- **Processing:**
  - `POST /api/session/next` → syllabus + mental model → build generation prompt →
    Ollama `/api/generate` (`stream:false`, `format:"json"`) → validate/coerce →
    de-duplicate via `question_hash` → return the next question.
  - `POST /api/session/answer` → deterministic check (objective) **or** rubric-graded
    Ollama call (subjective) → score 0–100 → update mental model → decide next
    difficulty + question type.
- **Output:** each turn renders one calm answer card: the verdict, the step-by-step
  solution, *how to think* about it, the misconception (if any), and the updated mastery
  bar. At session end: a summary with strengths, weak areas, and recommended next topics.

### Output schema — generated question (`lib/types.ts` / backend `schemas`)

```jsonc
{
  "question_id": "string",
  "question_hash": "string — stable hash to prevent repeats for this student",
  "class": "5",
  "subject": "Maths | English | Science",
  "topic": "string (topic_id or title)",
  "difficulty": 3,                       // 1..5
  "type": "mcq | short_answer | explain | fill_blank | true_false_reason | diagram | step_problem | word_problem | reasoning | match | spot_mistake | improve_answer",
  "question": "string — the prompt shown to the student",
  "options": ["string"],                 // [] for non-MCQ
  "expected_answer": "string",
  "explanation": "string — why the answer is what it is",
  "how_to_think": "string — the reasoning strategy, teaches the student",
  "common_mistake": "string — the trap students fall into",
  "skill_tags": ["string"],
  "estimated_time_seconds": 60
}
```

### Output schema — answer evaluation

```jsonc
{
  "correct": true,
  "score": 0,                            // 0..100
  "what_was_right": "string",
  "what_was_wrong": "string",
  "step_by_step": ["string"],
  "how_to_think": "string",
  "misconception": "string | null",
  "encouragement": "string — warm, never insulting",
  "next_difficulty": 3,                  // 1..5
  "next_type": "mcq | short_answer | ..."
}
```

---

## 4. Product philosophy (do not drift)

- **The adaptive engine + mental model are the heart.** Every feature serves the loop:
  pick → generate → answer → evaluate → update model → choose next.
- The AI **teaches** — it explains *how to think*, never just reveals the answer. Answers
  are encouraging and grade-appropriate.
- Local-only and private by default: no cloud calls, no telemetry, no external APIs.
- Quality over quantity: thoughtful, varied questions (not MCQ-only); poor output is
  regenerated; invalid JSON is repaired.

---

## 5. Build checklist

1. Identity filled here + in [`app.config.ts`](app.config.ts). ✅
2. Backend (FastAPI): auth, syllabus, mental_model, question_engine, evaluation, session,
   admin, ollama_client, guardrails — see [`PROMPT.md`](PROMPT.md) §5–13.
3. Frontend (Next.js): landing, login, dashboard, session, results, reports, admin pages,
   plus preloaded engagement games shown while Ollama generates.
4. Seed data: Class 5 Maths/Science/English syllabus, sample students + mental models,
   one admin account.
5. Reports (HTML + JSON export), one-command run, README with demo credentials.
