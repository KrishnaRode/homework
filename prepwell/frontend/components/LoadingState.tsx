"use client";

import { useEffect, useRef, useState } from "react";
import MemoryGrid from "@/components/games/MemoryGrid";
import OddOneOut from "@/components/games/OddOneOut";
import PatternNext from "@/components/games/PatternNext";
import CountShapes from "@/components/games/CountShapes";
import FindMatch from "@/components/games/FindMatch";
import { GAMES, type GameId, type GameOutcome } from "@/lib/brainGames";
import { BRAIN_LINES } from "@/lib/games";

// Shown while the real academic question is generated in the background. Rather than
// waiting on a single filler, we keep firing fresh GRAPHICAL puzzles — a different
// random game each round — until the parent swaps us out. Procedural generators plus
// a recently-seen guard make every puzzle fresh and non-repeating across the session.
// These are pure warm-ups: they are NOT scored and never touch academic indices.

function randomGameId(prev?: GameId): GameId {
  const pool = prev ? GAMES.filter((g) => g.id !== prev) : GAMES;
  return pool[Math.floor(Math.random() * pool.length)].id;
}

function randomLevel(): number {
  return 1 + Math.floor(Math.random() * 3); // keep warm-ups easy: levels 1–3
}

export default function LoadingState() {
  const [line, setLine] = useState(0);
  const [current, setCurrent] = useState<GameId>(() => randomGameId());
  const [level, setLevel] = useState(() => randomLevel());
  const [round, setRound] = useState(0); // remount key — forces a fresh puzzle
  const [solved, setSolved] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);
  const advanceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const id = setInterval(() => setLine((l) => (l + 1) % BRAIN_LINES.length), 1800);
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
    <div className="card animate-rise p-6">
      <div className="flex items-center gap-3">
        <span className="h-2.5 w-2.5 animate-soft-pulse rounded-full bg-accent" />
        <span className="text-sm text-text-muted">{BRAIN_LINES[line]}</span>
        {solved > 0 && (
          <span className="ml-auto rounded-full border border-border bg-panel px-2.5 py-0.5 text-xs text-text-faint">
            {solved} solved
          </span>
        )}
      </div>

      <div className="mt-6 rounded-xl border border-border-soft bg-bg-soft p-5">
        <div className="mb-4 flex items-center gap-2 text-xs uppercase tracking-wide text-text-faint">
          <span>{meta.emoji}</span>
          <span>{meta.name}</span>
          <span className="text-text-faint/60">· brain game while we get the next question ready</span>
        </div>

        <div className="grid min-h-[280px] place-items-center">
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
      </div>
    </div>
  );
}
