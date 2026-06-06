# Project Definition

> **Fill this in to start a new Sunday build.** It is the only spec you edit by hand.
> Mirror Section 1 into [`app.config.ts`](app.config.ts), then hand [`PROMPT.md`](PROMPT.md)
> to an AI coding agent to generate `app/`, `components/`, and `lib/`.

---

## 1. Identity (placeholders → `app.config.ts`)

| Placeholder            | Value (fill in)                |
| ---------------------- | ------------------------------ |
| `{{PRODUCT_NAME}}`     |                                |
| `{{TAGLINE}}`          |                                |
| `{{DESCRIPTION}}`      |                                |
| `{{OLLAMA_MODEL}}`     | e.g. `qwen2.5-coder`, `llama3.2` |
| `{{REPO_URL}}`         |                                |
| `{{API_ROUTE}}`        | e.g. `/api/explain`            |
| `{{PRIMARY_INPUT}}`    | e.g. "a SQL query"             |
| `{{PRIMARY_ACTION}}`   | e.g. "Explain"                 |

> `run.sh` / `run.bat` read `{{OLLAMA_MODEL}}` automatically from `app.config.ts`.

---

## 2. The problem this solves

_2-4 sentences: who is stuck, on what, and why doing it locally/free matters._

---

## 3. Input → Output contract

- **Input:** _what the user provides (`{{PRIMARY_INPUT}}`)._
- **Processing:** `POST {{API_ROUTE}}` → build prompt → Ollama `/api/generate`
  (`stream:false`, `format:"json"`) → validate/coerce.
- **Output:** _the structured result, rendered as one calm answer card._

### Output schema (`lib/types.ts`)

```jsonc
{
  // define the exact JSON the model must return
}
```

---

## 4. Product philosophy (do not drift)

- **The answer is the product.** No dashboards, sidebars, or feature overload.
- One screen: input → action → answer. The UI almost disappears.
- The AI **teaches** — it explains *why*, never just lists mechanics.

---

## 5. Reuse checklist

1. **Use this template** (GitHub → "Use this template") and clone it.
2. Fill **Section 1** here + [`app.config.ts`](app.config.ts).
3. Pick the model (`{{OLLAMA_MODEL}}`) that fits the task.
4. Define **Section 3**'s output schema.
5. Hand [`PROMPT.md`](PROMPT.md) to your AI agent to generate the app.
6. `./run.sh` (macOS/Linux) or `run.bat` (Windows) → demo → post. 🎬
