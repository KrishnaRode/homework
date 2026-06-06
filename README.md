# Sunday AI Template

The starter for the **Free AI. Real Problems. Every Sunday.** series — build a small,
beautiful, fully-local AI web app (Next.js + TypeScript + Tailwind v4 + Ollama) every week.

> This repo is **docs + scaffolding only**. The app code (`app/`, `components/`, `lib/`)
> is generated per product by handing [`PROMPT.md`](PROMPT.md) to an AI coding agent.
> See [`sql-query-explainer`](https://github.com/KrishnaRode/sql-query-explainer) for a
> finished example built from this template.

---

## What's in here

| File                           | Purpose                                                              |
| ------------------------------ | -------------------------------------------------------------------- |
| [`project.md`](project.md)     | Fill-in spec: identity placeholders + input/output contract          |
| [`PROMPT.md`](PROMPT.md)       | The reusable master build prompt (feed to your AI agent)             |
| [`design.md`](design.md)       | The fixed design system — keeps every build on-brand                 |
| [`app.config.ts`](app.config.ts) | Branding + model config skeleton (placeholders mirror `project.md`)|
| `run.sh` / `run.bat`           | One-command launchers (Ollama + deps + dev server) for mac/linux/win |
| `.gitignore`, `LICENSE`        | Standard repo hygiene (MIT)                                          |

---

## How to build a product from this template

1. **Use this template** on GitHub → clone your new repo.
2. **Fill** [`project.md`](project.md) Section 1 + the output schema, and mirror the
   identity into [`app.config.ts`](app.config.ts).
3. **Generate the app:** hand [`PROMPT.md`](PROMPT.md) (placeholders filled) to an AI
   coding agent. It produces `app/`, `components/`, `lib/`, and the build config.
4. **Run it:** `./run.sh` (macOS/Linux) or `run.bat` (Windows) — checks Node + Ollama,
   starts Ollama, pulls the model, installs deps, and launches at <http://localhost:3000>.
5. **Demo & post.** 🎬

---

## Prerequisites

- **Node.js 18.18+** (LTS) — <https://nodejs.org>
- **Ollama** — <https://ollama.com/download>

---

## Known-good stack (so generated apps build cleanly)

- **Next.js `^15.5`** (App Router) — avoid 15.1.x (security CVE)
- **React 19**
- **Tailwind CSS `^4.3`** with `@tailwindcss/postcss` — avoid 4.0.0 (scanner mismatch);
  define theme tokens in `globals.css` via `@theme` and use generated utilities
  (`bg-panel`, `text-text-muted`), not the `bg-[--color-panel]` arbitrary form
- **TypeScript 5**, strict mode

---

## License

MIT — use it, remix it, ship your own Sunday build.
