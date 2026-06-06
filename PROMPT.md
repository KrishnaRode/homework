# Reusable Build Prompt

This is the master prompt for the **Free AI. Real Problems. Every Sunday.** series.
Fill in the `{{PLACEHOLDERS}}` (they come from [`project.md`](project.md)) and hand the
whole thing to an AI coding agent to generate the next product on top of this template.

> Keep the philosophy, design, and quality sections **unchanged** — they are the brand.
> Only the placeholders and the "Output structure" / "Sample input" sections change per product.

---

## ▼ Fill these in first

```
{{PRODUCT_NAME}}    = "PrepWell — Learning Agent"
{{TAGLINE}}         = "Prepare smarter. Learn deeper."
{{PRIMARY_INPUT}}   = "a student's class + subject + topic, then their answers in a live session"
{{PRIMARY_ACTION}}  = "Practice (Start Adaptive Session)"
{{OLLAMA_MODEL}}    = "llama3.2:3b"   // installed locally; override with PREPWELL_MODEL
{{API_ROUTE}}       = "FastAPI /api — core loop: POST /api/session/next, POST /api/session/answer"
{{OUTPUT_SCHEMA}}   = see project.md §3 (generated-question + answer-evaluation schemas)
```

> **PrepWell is bigger than the single-screen template.** It is a two-service,
> local-first learning *platform* (Next.js + FastAPI + Ollama + SQLite/JSON). The brand,
> design system, and "the answer teaches" philosophy below still apply, but the full,
> authoritative 17-section build brief lives in [`prepwell/BUILD_BRIEF.md`](prepwell/BUILD_BRIEF.md)
> and the contract in [`project.md`](project.md). Treat those as the source of truth for
> architecture; treat the sections below as the design/quality bar.

---

## ▼ The prompt (copy from here down)

Build a complete, production-quality Next.js web application called:

**{{PRODUCT_NAME}}**

### Purpose

A minimalistic AI-powered web application: **{{TAGLINE}}** It runs entirely locally
using Ollama. This is part of a public "Free AI. Real Problems. Every Sunday." series.

The objective is NOT an enterprise platform. The objective IS the simplest, cleanest,
most beautiful experience possible: the user provides **{{PRIMARY_INPUT}}** and
immediately understands the result.

Think: Perplexity, Linear, Raycast, Vercel. Modern, premium, intelligent, effortless.

### Tech stack

- Next.js (latest stable), App Router, TypeScript, React
- Tailwind CSS v4
- Ollama local API — no database, no authentication, no paid APIs, no Docker for the MVP

### Product philosophy

**The result is the product.** NOT dashboards, analytics, panels, or feature overload.
YES clarity, simplicity, learning, elegance. The flow is: provide input → click
**{{PRIMARY_ACTION}}** → understand within 30 seconds. The UI should almost disappear
and let the answer shine.

### Design system

Follow [`design.md`](design.md) exactly — premium dark mode, navy undertones, soft
radial glow, generous spacing, calm. No neon, no clutter, subtle purposeful motion.
Single centered page, max width ~900px. Tokens live in `globals.css` via Tailwind
`@theme`; branding/model live in `app.config.ts`.

### Page layout

Single page, centered:

```
Series chip
{{PRODUCT_NAME}}            (large heading)
{{TAGLINE}}                 (sub-text)
──────────────────────────
Input area
──────────────────────────
[{{PRIMARY_ACTION}}]  [Sample]  [Clear]
──────────────────────────
AI Answer
```

No sidebars, no nav menus, no footer clutter.

### Input

Large, beautiful, responsive input appropriate to {{PRIMARY_INPUT}} (monospace editor
for code/SQL; clean textarea otherwise). Excellent focus state. Minimal controls:
**{{PRIMARY_ACTION}}**, **Sample**, **Clear**. Support ⌘/Ctrl+Enter to submit.

### The answer experience (most important)

Do NOT produce dry technical documentation. The AI should TEACH — explain *why*, not
just *what*, in warm, conversational, plain English, like a senior engineer mentoring a
junior one.

Render the structured result with clear sections and, where it fits, a single summary
badge (e.g. a complexity level). Define the exact sections in **{{OUTPUT_SCHEMA}}**.

### Ollama integration

Create `POST {{API_ROUTE}}`. Request body: `{ "input": "...", "model": "{{OLLAMA_MODEL}}" }`
(name the field to match the product). Default model: `{{OLLAMA_MODEL}}`.
Call `http://localhost:11434/api/generate` with `stream: false` and `format: "json"`.
Implement timeout handling, one retry for transient/parse failures, and graceful errors.
If Ollama is unavailable, surface: **"Ollama is not running. Start it using: ollama serve"**

### Prompt engineering

Create a reusable prompt builder in `lib/prompts.ts`. The model must return **JSON only**
matching **{{OUTPUT_SCHEMA}}**. Instruct it to: explain in plain English; never invent
facts or meanings; state assumptions explicitly when uncertain; be educational, concise,
and accurate. Parse defensively — strip fences, extract the JSON object, and coerce to a
guaranteed-valid typed shape.

### Error handling

Handle: empty input, invalid request, Ollama offline, model missing, timeout, malformed
AI response. Show friendly, code-aware messages with the fix (and a retry button).

### Loading experience

While generating: disable the action, show an elegant loader with rotating status lines
(e.g. "Reading input…", "Understanding…", "Building explanation…").

### Sample input

Include one realistic, meaningful **Sample** that exercises the interesting cases for
this domain, so the demo shines with one click.

### Code quality

TypeScript everywhere, reusable components, strong typing, no unused imports, no TODOs,
no mock implementations. Use this exact structure:

```
app/
  api/<route>/route.ts
  page.tsx  layout.tsx  globals.css
components/
  <Input>.tsx  <ActionButton>.tsx  <AnswerView>.tsx  LoadingState.tsx  ErrorMessage.tsx
lib/
  ollama.ts  prompts.ts  types.ts  sample.ts
app.config.ts
```

### README

Overview, features, architecture, prerequisites, Ollama install, model install
(`ollama pull {{OLLAMA_MODEL}}`), run (`npm install` / `npm run dev` or `./run.sh`),
and troubleshooting (Ollama not running, model not found, port conflicts).

### Final review before finishing

Review the whole codebase; fix TypeScript/import/lint issues; verify the API route works,
JSON parsing is robust, the layout is responsive, the dark theme is consistent, and the
answer experience is polished. Deliver a complete working project ready for GitHub and a
LinkedIn demo.

---

## Appendix — worked example: SQL Query Explainer

The reference implementation in this repo used this `{{OUTPUT_SCHEMA}}`:

```jsonc
{
  "executiveSummary": "string — 2-4 plain-English sentences on what the query achieves",
  "whatThisQueryIsDoing": ["string — step-by-step data flow and why each operation exists"],
  "businessInterpretation": "string — why a company/analyst would run this",
  "interestingObservations": ["string — joins, CTEs, window fns, perf, data-quality risks"],
  "complexity": "Easy | Moderate | Advanced"
}
```

Writing-style guidance given to the model (reuse this pattern for any domain):

- BAD: "The query performs a LEFT JOIN."
- GOOD: "The query starts with customer orders and then enriches them with customer
  details. A LEFT JOIN keeps orders visible even when customer info is missing."

See [`lib/prompts.ts`](lib/prompts.ts) for the full, working version.
