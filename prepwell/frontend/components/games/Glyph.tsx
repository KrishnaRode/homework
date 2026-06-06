"use client";
/* =============================================================================
 *  File:        frontend/components/games/Glyph.tsx
 *  Description: Shared SVG glyph renderer for the brain games.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import type { Glyph as GlyphData } from "@/lib/brainGames";

// Pure-SVG renderer for a Glyph (shape + color + rotation + scale).
// Shared by all three Brain Games so shapes look identical everywhere.
export default function Glyph({ glyph, size = 56 }: { glyph: GlyphData; size?: number }) {
  const s = glyph.scale;
  // Draw in a 100x100 viewBox, centred on (50,50).
  const c = 50;
  const r = 34 * s;
  let shape: React.ReactNode;

  if (glyph.shape === "circle") {
    shape = <circle cx={c} cy={c} r={r} fill={glyph.color} />;
  } else if (glyph.shape === "square") {
    const h = r * 0.92;
    shape = <rect x={c - h} y={c - h} width={h * 2} height={h * 2} rx={6} fill={glyph.color} />;
  } else if (glyph.shape === "triangle") {
    const pts = [
      [c, c - r],
      [c + r * 0.92, c + r * 0.7],
      [c - r * 0.92, c + r * 0.7],
    ]
      .map((p) => p.join(","))
      .join(" ");
    shape = <polygon points={pts} fill={glyph.color} />;
  } else if (glyph.shape === "diamond") {
    const pts = [
      [c, c - r],
      [c + r, c],
      [c, c + r],
      [c - r, c],
    ]
      .map((p) => p.join(","))
      .join(" ");
    shape = <polygon points={pts} fill={glyph.color} />;
  } else {
    // star
    const pts: string[] = [];
    for (let i = 0; i < 10; i++) {
      const radius = i % 2 === 0 ? r : r * 0.45;
      const angle = (Math.PI / 5) * i - Math.PI / 2;
      pts.push(`${c + radius * Math.cos(angle)},${c + radius * Math.sin(angle)}`);
    }
    shape = <polygon points={pts.join(" ")} fill={glyph.color} />;
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      style={{ transform: `rotate(${glyph.rotation}deg)`, transition: "transform 0.2s" }}
      aria-hidden
    >
      {shape}
    </svg>
  );
}
