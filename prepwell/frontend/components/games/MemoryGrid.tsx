"use client";
/* =============================================================================
 *  File:        frontend/components/games/MemoryGrid.tsx
 *  Description: Memory grid brain game.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useEffect, useMemo, useRef, useState } from "react";
import { genMemoryGrid, type GameOutcome } from "@/lib/brainGames";

type Phase = "memorise" | "recall" | "done";

// Working-memory game: lit tiles flash, then the player taps them back from memory.
export default function MemoryGrid({
  level,
  onDone,
}: {
  level: number;
  onDone: (o: GameOutcome) => void;
}) {
  const data = useMemo(() => genMemoryGrid(level), [level]);
  const litSet = useMemo(() => new Set(data.lit), [data]);
  const [phase, setPhase] = useState<Phase>("memorise");
  const [picked, setPicked] = useState<Set<number>>(new Set());
  const memoMs = 1200 + data.lit.length * 450;
  const start = useRef(Date.now());

  useEffect(() => {
    start.current = Date.now();
    setPhase("memorise");
    setPicked(new Set());
    const t = setTimeout(() => setPhase("recall"), memoMs);
    return () => clearTimeout(t);
  }, [data, memoMs]);

  function tap(i: number) {
    if (phase !== "recall" || picked.has(i)) return;
    const next = new Set(picked);
    next.add(i);
    setPicked(next);
    if (next.size >= data.lit.length) finish(next);
  }

  function finish(final: Set<number>) {
    setPhase("done");
    let hits = 0;
    final.forEach((i) => litSet.has(i) && hits++);
    const score = Math.round((hits / data.lit.length) * 100);
    const won = hits === data.lit.length;
    setTimeout(() => onDone({ score, won }), 700);
  }

  return (
    <div className="flex flex-col items-center">
      <p className="mb-4 text-sm text-text-muted">
        {phase === "memorise"
          ? "Memorise the lit tiles…"
          : phase === "recall"
            ? `Tap the ${data.lit.length} tiles you saw (${picked.size}/${data.lit.length})`
            : "Checking…"}
      </p>
      <div
        className="grid gap-2"
        style={{ gridTemplateColumns: `repeat(${data.size}, minmax(0, 1fr))` }}
      >
        {Array.from({ length: data.size * data.size }, (_, i) => {
          const isLit = litSet.has(i);
          const isPicked = picked.has(i);
          const reveal = phase === "memorise" || phase === "done";
          const showLit = reveal && isLit;
          const correct = phase === "done" && isPicked && isLit;
          const wrong = phase === "done" && isPicked && !isLit;
          return (
            <button
              key={i}
              onClick={() => tap(i)}
              disabled={phase !== "recall"}
              className={`h-14 w-14 rounded-xl border transition active:scale-95 sm:h-16 sm:w-16 ${
                correct
                  ? "border-emerald-400 bg-emerald-400/30"
                  : wrong
                    ? "border-rose-400 bg-rose-400/20"
                    : showLit
                      ? "border-accent bg-accent shadow-lg shadow-accent/30"
                      : isPicked
                        ? "border-accent bg-accent-soft/30"
                        : "border-border bg-bg-soft hover:bg-panel-hover"
              }`}
            />
          );
        })}
      </div>
    </div>
  );
}
