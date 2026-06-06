# Design System

The look of every "Free AI. Real Problems. Every Sunday." product. Reuse this as-is
across builds — consistency is part of the brand.

**Feel:** modern, premium, intelligent, effortless. Think Perplexity · Linear · Raycast · Vercel.

---

## Theme — premium dark mode

Not gaming. Not cyberpunk. Not flashy. Modern SaaS.

- Deep black background with slight **navy** undertones
- Soft radial gradients + subtle glow behind content (never neon)
- Excellent contrast, generous whitespace, calm

**Avoid:** rainbow gradients, bright neon everywhere, excessive animation, clutter.

---

## Tokens

Defined once in [`app/globals.css`](app/globals.css) via Tailwind v4 `@theme`. Each
`--color-*` token automatically becomes a utility (`bg-panel`, `text-text-muted`,
`border-border`, `text-accent`, …).

| Token                   | Value     | Used for                          |
| ----------------------- | --------- | --------------------------------- |
| `--color-bg`            | `#05060a` | Page background                   |
| `--color-bg-soft`       | `#0a0c14` | Inset / quoted blocks             |
| `--color-panel`         | `#0e1119` | Cards, editor, buttons            |
| `--color-panel-hover`   | `#141826` | Hover / skeleton fills            |
| `--color-border`        | `#1c2333` | Card & control borders            |
| `--color-border-soft`   | `#161b28` | Subtle dividers                   |
| `--color-text`          | `#e8ebf2` | Primary text                      |
| `--color-text-muted`    | `#9aa3b5` | Body / secondary text             |
| `--color-text-faint`    | `#5d6678` | Hints, captions, labels           |
| `--color-accent`        | `#6d8bff` | Primary action, highlights        |
| `--color-accent-soft`   | `#3d57c9` | Glow, focus ring, gradients       |

The ambient navy glow lives in `body::before` (two soft radial gradients).

---

## Typography

- System sans stack for UI (`--font-sans`), monospace for code/SQL (`--font-mono`).
- Large, tight-tracking headings; comfortable reading width (~`max-w-xl` for prose).
- Strong hierarchy: uppercase micro-labels for sections, `text-balance` headlines.

---

## Layout

- Single page. Centered. **Max width ~900px** (`max-w-[900px]`).
- Structure, top to bottom: **Series chip → Title → Tagline → Input → Actions → Answer → Footer.**
- No sidebars, no nav menus, no footer clutter.

---

## Components

| Component                                            | Role                                            |
| ---------------------------------------------------- | ----------------------------------------------- |
| [`SqlEditor`](components/SqlEditor.tsx)              | Monospace input with a "code window" header     |
| [`ExplainButton`](components/ExplainButton.tsx)      | Primary action with spinner + idle states       |
| [`LoadingState`](components/LoadingState.tsx)        | Rotating status lines + skeleton                |
| [`ErrorMessage`](components/ErrorMessage.tsx)        | Friendly, code-aware error with a retry         |
| [`ExplanationView`](components/ExplanationView.tsx)  | The answer: sections + complexity badge         |

---

## Motion

- Subtle, smooth, purposeful only. `animate-rise` for entrances; soft pulse for loading.
- Micro-interactions: button `active:scale`, hover brighten, focus-within border.
- Honor `prefers-reduced-motion` (handled globally in `globals.css`).

---

## States to always design for

`empty` · `loading` · `error` · `success`. Each has a dedicated, polished treatment —
the empty state invites action, the error state explains the fix.
