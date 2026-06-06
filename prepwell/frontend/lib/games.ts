/* =============================================================================
 *  File:        frontend/lib/games.ts
 *  Description: Loading/brain-game status line copy.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
// Loading/brain-training framing strings shown while the next academic question is
// generated in the background. The actual wait-time fillers are now GRAPHICAL brain
// games (see lib/brainGames.ts + components/games/*) — there are no text quizzes here
// anymore, so a fast solver always gets a fresh visual puzzle, never a repeated one.

export const LOADING_LINES = [
  "Reading your progress…",
  "Thinking about what helps you most…",
  "Designing the next question…",
  "Making it just the right difficulty…",
  "Almost ready…",
];

// Brain-training framing shown above the graphical warm-up while the real question
// is being prepared.
export const BRAIN_LINES = [
  "Let's exercise your brain 🧠",
  "Warming up those neurons…",
  "Keep that mind sharp 💪",
  "A quick rep for your reasoning…",
  "Stay in the zone — one more!",
  "Sharpening your thinking…",
];
