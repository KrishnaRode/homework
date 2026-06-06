"use client";
/* =============================================================================
 *  File:        frontend/components/games/PatternNext.tsx
 *  Description: Pattern-completion brain game.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useMemo, useState } from "react";
import { genPatternNext, type GameOutcome } from "@/lib/brainGames";
import Glyph from "./Glyph";

// Sequential-reasoning game: work out which shape continues the pattern.
export default function PatternNext({
  level,
  onDone,
}: {
  level: number;
  onDone: (o: GameOutcome) => void;
}) {
  const data = useMemo(() => genPatternNext(level), [level]);
  const [picked, setPicked] = useState<number | null>(null);

  function tap(i: number) {
    if (picked !== null) return;
    setPicked(i);
    const won = i === data.answerIndex;
    setTimeout(() => onDone({ score: won ? 100 : 0, won }), 800);
  }

  return (
    <div className="flex flex-col items-center">
      <p className="mb-4 text-sm text-text-muted">Which shape comes next?</p>

      <div className="mb-6 flex items-center gap-2 rounded-2xl border border-border bg-bg-soft p-3">
        {data.sequence.map((g, i) => (
          <div key={i} className="grid h-14 w-14 place-items-center">
            <Glyph glyph={g} size={44} />
          </div>
        ))}
        <div className="grid h-14 w-14 place-items-center rounded-xl border-2 border-dashed border-border text-2xl text-text-faint">
          ?
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {data.options.map((g, i) => {
          const reveal = picked !== null;
          const correct = reveal && i === data.answerIndex;
          const wrongPick = reveal && picked === i && i !== data.answerIndex;
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
