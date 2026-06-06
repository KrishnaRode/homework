"use client";
/* =============================================================================
 *  File:        frontend/components/LoadingState.tsx
 *  Description: Honest 'preparing question' status with an optional brain game.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useEffect, useRef, useState } from "react";
import MemoryGrid from "@/components/games/MemoryGrid";
import OddOneOut from "@/components/games/OddOneOut";
import PatternNext from "@/components/games/PatternNext";
import CountShapes from "@/components/games/CountShapes";
import FindMatch from "@/components/games/FindMatch";
import { GAMES, type GameId, type GameOutcome } from "@/lib/brainGames";
import { LOADING_LINES } from "@/lib/games";

// Shown while the real academic question is generated in the background. The honest
// "Preparing your question…" status is the focus — this is a learning app, and the
// student is always told their question is on its way and will open the instant it's
// ready (the parent swaps this view out for the question automatically). Underneath,
// an OPTIONAL brain game is offered as a small distraction for the short wait. Those
// puzzles are pure warm-ups: NOT scored, and they never touch academic indices.

function randomGameId(prev?: GameId): GameId {
  const pool = prev ? GAMES.filter((g) => g.id !== prev) : GAMES;
  return pool[Math.floor(Math.random() * pool.length)].id;
}

function randomLevel(): number {
  return 1 + Math.floor(Math.random() * 3); // keep warm-ups easy: levels 1–3
}

export default function LoadingState({ first = false }: { first?: boolean }) {
  const [line, setLine] = useState(0);
  const [current, setCurrent] = useState<GameId>(() => randomGameId());
  const [level, setLevel] = useState(() => randomLevel());
  const [round, setRound] = useState(0); // remount key — forces a fresh puzzle
  const [solved, setSolved] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [showGame, setShowGame] = useState(false);
  const advanceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const id = setInterval(() => setLine((l) => (l + 1) % LOADING_LINES.length), 2200);
    return () => clearInterval(id);
  }, []);

  useEffect(
    () => () => {
      if (advanceTimer.current) clearTimeout(advanceTimer.current);
    },
    [],
  );

  function handleDone(outcome: GameOutcome) {
    if (outcome.won) setSolved((s) => s + 1);
    setFeedback(outcome.won ? "Nice! 🎉" : "Good try!");
    advanceTimer.current = setTimeout(() => {
      setCurrent((prev) => randomGameId(prev));
      setLevel(randomLevel());
      setRound((r) => r + 1);
      setFeedback(null);
    }, 800);
  }

  const meta = GAMES.find((g) => g.id === current)!;

  return (
    <div className="card animate-rise p-7">
      {/* Primary status — honest and prominent. This is a learning app: the student's
          question is the headline, and it auto-opens the moment it's ready. */}
      <div className="text-center">
        <div className="mx-auto flex w-fit items-center gap-2.5 rounded-full border border-border bg-bg-soft px-4 py-1.5">
          <span className="flex gap-1" aria-hidden>
            <span className="h-2 w-2 animate-soft-pulse rounded-full bg-accent" style={{ animationDelay: "0ms" }} />
            <span className="h-2 w-2 animate-soft-pulse rounded-full bg-accent" style={{ animationDelay: "200ms" }} />
            <span className="h-2 w-2 animate-soft-pulse rounded-full bg-accent" style={{ animationDelay: "400ms" }} />
          </span>
          <span className="text-xs font-medium uppercase tracking-wide text-text-muted">
            {first ? "Getting started" : "Working on it"}
          </span>
        </div>

        <h2 className="mt-4 text-2xl font-bold">
          Preparing your {first ? "first" : "next"} question…
        </h2>
        <p className="mt-2 text-sm text-text-muted">{LOADING_LINES[line]}</p>
        <p className="mt-1 text-xs text-text-faint">
          It’ll open here automatically the moment it’s ready.
        </p>
      </div>

      {/* Secondary, optional: a tiny brain game to pass the short wait. Clearly
          marked as a sidebar to the real task — and never scored. */}
      <div className="mt-7 rounded-xl border border-border-soft bg-bg-soft/60 p-4">
        {!showGame ? (
          <div className="flex flex-wrap items-center justify-center gap-3 text-center">
            <span className="text-sm text-text-muted">
              While you wait, fancy a quick brain teaser? 🧠
            </span>
            <button
              onClick={() => setShowGame(true)}
              className="rounded-full border border-border bg-panel px-4 py-1.5 text-sm font-medium text-accent transition hover:bg-panel-hover"
            >
              Play a quick game
            </button>
          </div>
        ) : (
          <>
            <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-wide text-text-faint">
              <span>{meta.emoji}</span>
              <span>{meta.name}</span>
              <span className="text-text-faint/60">· optional · just for fun</span>
              {solved > 0 && (
                <span className="ml-auto rounded-full border border-border bg-panel px-2.5 py-0.5 normal-case text-text-faint">
                  {solved} solved
                </span>
              )}
            </div>

            <div className="grid min-h-[240px] place-items-center">
              {feedback ? (
                <div className="text-2xl font-semibold">{feedback}</div>
              ) : current === "memory_grid" ? (
                <MemoryGrid key={round} level={level} onDone={handleDone} />
              ) : current === "odd_one_out" ? (
                <OddOneOut key={round} level={level} onDone={handleDone} />
              ) : current === "pattern_next" ? (
                <PatternNext key={round} level={level} onDone={handleDone} />
              ) : current === "count_shapes" ? (
                <CountShapes key={round} level={level} onDone={handleDone} />
              ) : (
                <FindMatch key={round} level={level} onDone={handleDone} />
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
