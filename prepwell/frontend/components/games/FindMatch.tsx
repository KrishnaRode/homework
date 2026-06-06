"use client";
/* =============================================================================
 *  File:        frontend/components/games/FindMatch.tsx
 *  Description: Find-the-match brain game.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useMemo, useState } from "react";
import { genFindMatch, type GameOutcome } from "@/lib/brainGames";
import Glyph from "./Glyph";

// Matching game: find the one cell that exactly matches the target glyph.
export default function FindMatch({
  level,
  onDone,
}: {
  level: number;
  onDone: (o: GameOutcome) => void;
}) {
  const data = useMemo(() => genFindMatch(level), [level]);
  const [picked, setPicked] = useState<number | null>(null);

  function tap(i: number) {
    if (picked !== null) return;
    setPicked(i);
    const won = i === data.matchIndex;
    setTimeout(() => onDone({ score: won ? 100 : 0, won }), 800);
  }

  return (
    <div className="flex flex-col items-center">
      <p className="mb-3 text-sm text-text-muted">Find the exact twin of this shape:</p>

      <div className="mb-6 grid h-20 w-20 place-items-center rounded-2xl border-2 border-accent bg-bg-soft">
        <Glyph glyph={data.target} size={52} />
      </div>

      <div
        className="grid gap-3"
        style={{ gridTemplateColumns: `repeat(${data.cols}, minmax(0, 1fr))` }}
      >
        {data.cells.map((g, i) => {
          const reveal = picked !== null;
          const correct = reveal && i === data.matchIndex;
          const wrongPick = reveal && picked === i && i !== data.matchIndex;
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
