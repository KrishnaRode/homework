/* =============================================================================
 *  File:        frontend/app.config.ts
 *  Description: Frontend branding mirror (name, tagline, series, repo URL).
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
/** Branding mirror for the frontend (keep in sync with repo-root app.config.ts). */
export const appConfig = {
  name: "PrepWell",
  fullName: "PrepWell — Learning Agent",
  tagline: "Prepare smarter. Learn deeper.",
  description:
    "A private AI tutor on your laptop that understands how every student learns.",
  series: "Free AI. Real Problems. Every Sunday.",
  repoUrl: "https://github.com/KrishnaRode/homework",
} as const;
