"use client";
/* =============================================================================
 *  File:        frontend/components/games/OddOneOut.tsx
 *  Description: Odd-one-out brain game.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useMemo, useState } from "react";
import { genOddOneOut, type GameOutcome } from "@/lib/brainGames";
import Glyph from "./Glyph";

// Visual-discrimination game: tap the one shape that differs from the rest.
export default function OddOneOut({
  level,
  onDone,
}: {
  level: number;
  onDone: (o: GameOutcome) => void;
}) {
  const data = useMemo(() => genOddOneOut(level), [level]);
  const [picked, setPicked] = useState<number | null>(null);

  function tap(i: number) {
    if (picked !== null) return;
    setPicked(i);
    const won = i === data.oddIndex;
    setTimeout(() => onDone({ score: won ? 100 : 0, won }), 800);
  }

  return (
    <div className="flex flex-col items-center">
      <p className="mb-4 text-sm text-text-muted">Tap the shape that doesn&apos;t belong.</p>
      <div
        className="grid gap-3"
        style={{ gridTemplateColumns: `repeat(${data.cols}, minmax(0, 1fr))` }}
      >
        {data.cells.map((g, i) => {
          const isPicked = picked === i;
          const reveal = picked !== null;
          const correct = reveal && i === data.oddIndex;
          const wrongPick = reveal && isPicked && i !== data.oddIndex;
          return (
            <button
              key={i}
              onClick={() => tap(i)}
              disabled={reveal}
              className={`grid h-20 w-20 place-items-center rounded-2xl border transition active:scale-95 ${
                correct
                  ? "border-emerald-400 bg-emerald-400/20"
                  : wrongPick
                    ? "border-rose-400 bg-rose-400/20"
                    : "border-border bg-bg-soft hover:bg-panel-hover"
              }`}
            >
              <Glyph glyph={g} size={48} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
