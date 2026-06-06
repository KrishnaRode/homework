/**
 * ─────────────────────────────────────────────────────────────
 *  PRODUCT IDENTITY  —  fill these in for the new Sunday build
 * ─────────────────────────────────────────────────────────────
 *  Single source of truth for branding & model config.
 *  The values here must match the table in project.md.
 *  Replace every {{PLACEHOLDER}} below, then run PROMPT.md
 *  through your AI coding agent to generate the app.
 */
export const appConfig = {
  /** Product name shown in the hero + browser tab. */
  name: "{{PRODUCT_NAME}}",

  /** One-line value proposition under the title. */
  tagline: "{{TAGLINE}}",

  /** Longer description for <meta> tags + README. */
  description: "{{DESCRIPTION}}",

  /** The Ollama model pulled + used by default (run.sh/run.bat read this). */
  defaultModel: "{{OLLAMA_MODEL}}",

  /** Series branding — keep as-is. */
  series: "Free AI. Real Problems. Every Sunday.",

  /** Public repo URL. */
  repoUrl: "{{REPO_URL}}",
} as const;

export type AppConfig = typeof appConfig;
