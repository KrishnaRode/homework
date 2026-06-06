"use client";
/* =============================================================================
 *  File:        frontend/app/games/page.tsx
 *  Description: Standalone brain-games arcade (non-academic warm-ups).
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import MemoryGrid from "@/components/games/MemoryGrid";
import OddOneOut from "@/components/games/OddOneOut";
import PatternNext from "@/components/games/PatternNext";
import CountShapes from "@/components/games/CountShapes";
import FindMatch from "@/components/games/FindMatch";
import { BrandHeader } from "@/components/Brand";
import ThemeToggle from "@/components/ThemeToggle";
import { GAMES, type GameId, type GameOutcome } from "@/lib/brainGames";
import { api } from "@/lib/api";
import { getSession } from "@/lib/auth";
import type { BrainStats } from "@/lib/types";

type Active = GameId | "random" | null;

// Each game flaunts its own colour.
const GAME_COLOR: Record<string, string> = {
  memory_grid: "var(--joy-blue)",
  odd_one_out: "var(--joy-pink)",
  pattern_next: "var(--joy-green)",
  count_shapes: "var(--joy-orange)",
  find_match: "var(--joy-teal)",
};

function pickRandom(): GameId {
  return GAMES[Math.floor(Math.random() * GAMES.length)].id;
}

export default function GamesHub() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [brain, setBrain] = useState<BrainStats | null>(null);
  const [active, setActive] = useState<Active>(null);
  const [current, setCurrent] = useState<GameId>("memory_grid");
  const [level, setLevel] = useState(1);
  const [round, setRound] = useState(0); // forces a fresh puzzle each play
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadScore = useCallback(() => {
    api.get<{ brain: BrainStats }>("/api/games/score").then((r) => setBrain(r.brain));
  }, []);

  useEffect(() => {
    const s = getSession();
    if (!s || s.role !== "student") {
      router.replace("/login");
      return;
    }
    setReady(true);
    loadScore();
  }, [router, loadScore]);

  function startGame(which: Active) {
    setActive(which);
    setCurrent(which === "random" ? pickRandom() : (which as GameId));
    setLevel(1);
    setRound((r) => r + 1);
    setFeedback(null);
  }

  function handleDone(outcome: GameOutcome) {
    const startedAt = Date.now();
    api
      .post<{ brain: BrainStats }>("/api/games/result", {
        game: current,
        score: outcome.score,
        won: outcome.won,
        duration_seconds: Math.round((Date.now() - startedAt) / 1000),
      })
      .then((r) => setBrain(r.brain))
      .catch(() => loadScore());

    setFeedback(outcome.won ? "Nice! ✅" : "Not quite — try the next one.");
    setLevel((l) => (outcome.won ? Math.min(10, l + 1) : Math.max(1, l - 1)));
    setTimeout(() => {
      setFeedback(null);
      setCurrent(active === "random" ? pickRandom() : current);
      setRound((r) => r + 1);
    }, 900);
  }

  function exitGame() {
    setActive(null);
    loadScore();
  }

  if (!ready) {
    return <div className="grid min-h-screen place-items-center text-text-muted">Loading…</div>;
  }

  const meta = GAMES.find((g) => g.id === current)!;

  return (
    <div className="min-h-screen">
      <BrandHeader
        right={
          <>
            <ThemeToggle />
            <button
              onClick={() => router.push("/dashboard")}
              className="rounded-lg border border-border bg-panel px-3 py-1.5 text-sm text-text-muted transition hover:bg-panel-hover hover:text-text"
            >
              Dashboard
            </button>
          </>
        }
      />

      <main className="mx-auto max-w-[900px] px-5 pt-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Brain Games 🧠</h1>
            <p className="mt-1.5 text-text-muted">
              Quick reasoning puzzles. Your brain score is separate — it never affects your
              learning report.
            </p>
          </div>
          {brain && (
            <div className="flex gap-2">
              <Stat label="Brain points" value={brain.points} tint="var(--joy-purple)" />
              <Stat label="Streak" value={brain.current_streak} tint="var(--joy-orange)" />
              <Stat label="Best" value={brain.best_streak} tint="var(--joy-teal)" />
            </div>
          )}
        </div>

        {active ? (
          <div className="card mt-8 p-6">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-wide text-text-faint">
                  {active === "random" ? "Random mix" : meta.skill}
                </div>
                <div className="text-lg font-semibold">
                  {meta.emoji} {meta.name} · Level {level}
                </div>
              </div>
              <button
                onClick={exitGame}
                className="rounded-lg border border-border bg-panel px-3 py-1.5 text-sm text-text-muted transition hover:bg-panel-hover hover:text-text"
              >
                Done
              </button>
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
        ) : (
          <>
            <button
              onClick={() => startGame("random")}
              className="mt-8 flex w-full items-center justify-between rounded-2xl px-6 py-5 text-left text-white shadow-lg transition hover:opacity-95 hover:-translate-y-0.5 active:scale-[0.99]"
              style={{
                background:
                  "linear-gradient(100deg, var(--joy-red), var(--joy-orange) 30%, var(--joy-purple) 65%, var(--joy-blue))",
              }}
            >
              <div>
                <div className="text-lg font-semibold">🎲 Random Mix</div>
                <div className="text-sm text-white/85">
                  A surprise puzzle each round, getting harder as you win.
                </div>
              </div>
              <span className="text-2xl">→</span>
            </button>

            <h2 className="mb-3 mt-10 text-sm uppercase tracking-wide text-text-faint">
              Or pick a game
            </h2>
            <div className="grid gap-3 sm:grid-cols-3">
              {GAMES.map((g) => {
                const tint = GAME_COLOR[g.id] || "var(--accent)";
                return (
                  <button
                    key={g.id}
                    onClick={() => startGame(g.id)}
                    style={{ ["--tint"]: tint } as React.CSSProperties}
                    className="card-pop p-5 text-left transition hover:-translate-y-0.5 active:scale-[0.99]"
                  >
                    <div
                      className="grid h-12 w-12 place-items-center rounded-2xl text-2xl"
                      style={{ background: `color-mix(in srgb, ${tint} 22%, transparent)` }}
                    >
                      {g.emoji}
                    </div>
                    <div className="mt-2 font-semibold">{g.name}</div>
                    <div className="text-xs font-semibold uppercase tracking-wide" style={{ color: tint }}>
                      {g.skill}
                    </div>
                    <div className="mt-2 text-sm text-text-muted">{g.blurb}</div>
                    {brain?.by_game[g.id] && (
                      <div className="mt-3 text-xs text-text-faint">
                        Played {brain.by_game[g.id].played} · best {brain.by_game[g.id].best}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function Stat({ label, value, tint = "var(--accent)" }: { label: string; value: number; tint?: string }) {
  return (
    <div
      className="rounded-xl border px-4 py-2 text-center"
      style={{
        borderColor: `color-mix(in srgb, ${tint} 40%, var(--border))`,
        background: `color-mix(in srgb, ${tint} 12%, transparent)`,
      }}
    >
      <div className="text-xl font-bold tabular-nums" style={{ color: tint }}>
        {value}
      </div>
      <div className="text-[10px] uppercase tracking-wide text-text-faint">{label}</div>
    </div>
  );
}
