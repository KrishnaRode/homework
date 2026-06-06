"use client";

import { useMemo, useState } from "react";
import { genCountShapes, type GameOutcome, type Glyph as GlyphData } from "@/lib/brainGames";
import Glyph from "./Glyph";

const SHAPE_LABEL: Record<string, string> = {
  circle: "circles",
  square: "squares",
  triangle: "triangles",
  diamond: "diamonds",
  star: "stars",
};

// Visual-counting game: count how many of one shape appear in the grid.
export default function CountShapes({
  level,
  onDone,
}: {
  level: number;
  onDone: (o: GameOutcome) => void;
}) {
  const data = useMemo(() => genCountShapes(level), [level]);
  const [picked, setPicked] = useState<number | null>(null);

  // A clean reference glyph for the "count the ___" hint.
  const hintGlyph: GlyphData = { shape: data.targetShape, color: "var(--accent)", rotation: 0, scale: 1 };

  function tap(n: number) {
    if (picked !== null) return;
    setPicked(n);
    const won = n === data.answer;
    setTimeout(() => onDone({ score: won ? 100 : 0, won }), 800);
  }

  return (
    <div className="flex flex-col items-center">
      <p className="mb-3 flex items-center gap-2 text-sm text-text-muted">
        How many <Glyph glyph={hintGlyph} size={22} /> {SHAPE_LABEL[data.targetShape]} do you see?
      </p>

      <div
        className="mb-6 grid gap-2 rounded-2xl border border-border bg-bg-soft p-3"
        style={{ gridTemplateColumns: `repeat(${data.cols}, minmax(0, 1fr))` }}
      >
        {data.cells.map((g, i) => (
          <div key={i} className="grid h-14 w-14 place-items-center">
            <Glyph glyph={g} size={40} />
          </div>
        ))}
      </div>

      <div className="flex flex-wrap justify-center gap-3">
        {data.options.map((n) => {
          const reveal = picked !== null;
          const correct = reveal && n === data.answer;
          const wrongPick = reveal && picked === n && n !== data.answer;
          return (
            <button
              key={n}
              onClick={() => tap(n)}
              disabled={reveal}
              className={`grid h-16 w-16 place-items-center rounded-2xl border text-2xl font-bold tabular-nums transition active:scale-95 ${
                correct
                  ? "border-emerald-400 bg-emerald-400/20 text-emerald-500"
                  : wrongPick
                    ? "border-rose-400 bg-rose-400/20 text-rose-500"
                    : "border-border bg-panel hover:bg-panel-hover"
              }`}
            >
              {n}
            </button>
          );
        })}
      </div>
    </div>
  );
}
