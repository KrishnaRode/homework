/**
 * ─────────────────────────────────────────────────────────────
 *  PRODUCT IDENTITY  —  PrepWell — Learning Agent
 * ─────────────────────────────────────────────────────────────
 *  Single source of truth for branding & model config.
 *  Mirrors the identity table in project.md.
 *  Note: PrepWell ships as a two-service app (Next.js + FastAPI).
 *  The frontend talks to the FastAPI backend; the backend owns
 *  the Ollama integration. Keep `defaultModel` in sync with the
 *  backend's PREPWELL_MODEL env (see prepwell/backend/.env.example).
 */
export const appConfig = {
  /** Product name shown in the hero + browser tab. */
  name: "PrepWell — Learning Agent",

  /** One-line value proposition under the title. */
  tagline: "Prepare smarter. Learn deeper.",

  /** Longer description for <meta> tags + README. */
  description:
    "PrepWell is a free, local-first AI learning agent for school students. " +
    "For any class/standard it generates unlimited personalized practice in " +
    "Mathematics, English, and Science — adapting every question to how the " +
    "student actually performs. A private AI tutor on your laptop that " +
    "understands how every student learns.",

  /** The Ollama model used by default (installed locally; no cloud). */
  defaultModel: "llama3.2:3b",

  /** Series branding — keep as-is. */
  series: "Free AI. Real Problems. Every Sunday.",

  /** Public repo URL. */
  repoUrl: "https://github.com/KrishnaRode/homework",
} as const;

export type AppConfig = typeof appConfig;
