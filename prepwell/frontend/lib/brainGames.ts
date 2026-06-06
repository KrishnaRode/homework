// Brain Games — deterministic, client-side reasoning puzzle generators.
// No LLM, no network: everything is generated locally for instant, offline play.

export type GameId =
  | "memory_grid"
  | "odd_one_out"
  | "pattern_next"
  | "count_shapes"
  | "find_match";

export interface GameMeta {
  id: GameId;
  name: string;
  skill: string;
  blurb: string;
  emoji: string;
}

export const GAMES: GameMeta[] = [
  { id: "memory_grid", name: "Memory Grid", skill: "Working memory", emoji: "🧠",
    blurb: "Memorise the lit tiles, then tap them back." },
  { id: "odd_one_out", name: "Odd One Out", skill: "Visual discrimination", emoji: "🔍",
    blurb: "Spot the shape that doesn't belong." },
  { id: "pattern_next", name: "What Comes Next", skill: "Sequential reasoning", emoji: "➡️",
    blurb: "Work out the next shape in the pattern." },
  { id: "count_shapes", name: "Count the Shapes", skill: "Visual counting", emoji: "🔢",
    blurb: "Count how many of one shape are hidden in the mix." },
  { id: "find_match", name: "Find the Twin", skill: "Matching", emoji: "👯",
    blurb: "Find the one shape that exactly matches the target." },
];

export interface GameOutcome {
  score: number; // 0-100
  won: boolean;
}

// ---- shared helpers ---------------------------------------------------------
export const PALETTE = ["#6ea8fe", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb923c"];
export type ShapeName = "circle" | "square" | "triangle" | "diamond" | "star";
export const SHAPES: ShapeName[] = ["circle", "square", "triangle", "diamond", "star"];

export interface Glyph {
  shape: ShapeName;
  color: string;
  rotation: number;
  scale: number;
}

export function randInt(maxExclusive: number): number {
  return Math.floor(Math.random() * maxExclusive);
}

export function sample<T>(arr: T[]): T {
  return arr[randInt(arr.length)];
}

export function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = randInt(i + 1);
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function glyphsEqual(a: Glyph, b: Glyph): boolean {
  return a.shape === b.shape && a.color === b.color && a.rotation === b.rotation && a.scale === b.scale;
}

// A fully random glyph — used by the counting/matching games that fill a grid
// with assorted shapes rather than variations on a single base.
export function randomGlyph(): Glyph {
  return {
    shape: sample(SHAPES),
    color: sample(PALETTE),
    rotation: sample([0, 45, 90, 135, 180, 225, 270, 315]),
    scale: 1,
  };
}

// ---- uniqueness guard -------------------------------------------------------
// Each generator is procedurally random; this guard additionally ensures a freshly
// generated puzzle hasn't been shown in the recent window, so brain games never
// repeat back-to-back within a session.
function glyphSig(g: Glyph): string {
  return `${g.shape}|${g.color}|${g.rotation}|${g.scale}`;
}

function makeDedup(max: number) {
  const seen: string[] = [];
  return function dedup<T>(gen: () => T, sig: (v: T) => string): T {
    let v = gen();
    let guard = 0;
    while (seen.includes(sig(v)) && guard++ < 50) v = gen();
    seen.push(sig(v));
    if (seen.length > max) seen.splice(0, seen.length - max);
    return v;
  };
}

// ---- Memory Grid ------------------------------------------------------------
export interface MemoryGridData {
  size: number; // grid is size x size
  lit: number[]; // cell indices that are lit
}

function _genMemoryGrid(level: number): MemoryGridData {
  const size = level >= 6 ? 5 : 4;
  const count = Math.min(size * size - 2, 4 + Math.floor(level / 2));
  const all = shuffle(Array.from({ length: size * size }, (_, i) => i));
  return { size, lit: all.slice(0, count).sort((a, b) => a - b) };
}

const _memDedup = makeDedup(16);
export function genMemoryGrid(level: number): MemoryGridData {
  return _memDedup(
    () => _genMemoryGrid(level),
    (d) => `${d.size}:${d.lit.join(",")}`,
  );
}

// ---- Odd One Out ------------------------------------------------------------
export interface OddOneOutData {
  cols: number;
  cells: Glyph[];
  oddIndex: number;
}

function _genOddOneOut(level: number): OddOneOutData {
  const cols = level >= 5 ? 4 : 3;
  const rows = level >= 3 ? 3 : 2;
  const total = cols * rows;
  const base: Glyph = {
    shape: sample(SHAPES),
    color: sample(PALETTE),
    rotation: sample([0, 45, 90, 135]),
    scale: 1,
  };
  const cells: Glyph[] = Array.from({ length: total }, () => ({ ...base }));
  const oddIndex = randInt(total);

  // Alter exactly one attribute so the odd cell is unambiguous but not obvious.
  const dimension = sample(["shape", "color", "rotation"] as const);
  const odd: Glyph = { ...base };
  if (dimension === "shape") {
    odd.shape = sample(SHAPES.filter((s) => s !== base.shape));
  } else if (dimension === "color") {
    odd.color = sample(PALETTE.filter((c) => c !== base.color));
  } else {
    odd.rotation = sample([0, 45, 90, 135].filter((r) => r !== base.rotation));
  }
  cells[oddIndex] = odd;
  return { cols, cells, oddIndex };
}

const _oooDedup = makeDedup(16);
export function genOddOneOut(level: number): OddOneOutData {
  return _oooDedup(
    () => _genOddOneOut(level),
    (d) => {
      const base = d.cells[d.oddIndex === 0 ? 1 : 0];
      return `${d.cols}:${d.oddIndex}:${glyphSig(base)}:${glyphSig(d.cells[d.oddIndex])}`;
    },
  );
}

// ---- What Comes Next --------------------------------------------------------
export interface PatternData {
  sequence: Glyph[];
  options: Glyph[];
  answerIndex: number;
}

function _genPatternNext(level: number): PatternData {
  const visible = level >= 4 ? 4 : 3;
  const rule = sample(["rotate", "color", "grow"] as const);
  const shape = sample(SHAPES.filter((s) => s !== "circle")); // circle hides rotation
  const baseColor = sample(PALETTE);
  const colorOrder = shuffle(PALETTE);

  const at = (step: number): Glyph => {
    if (rule === "rotate") {
      const dir = 45;
      return { shape, color: baseColor, rotation: (step * dir) % 360, scale: 1 };
    }
    if (rule === "color") {
      return { shape, color: colorOrder[step % colorOrder.length], rotation: 0, scale: 1 };
    }
    // grow
    return { shape, color: baseColor, rotation: 0, scale: 0.6 + step * 0.18 };
  };

  const sequence = Array.from({ length: visible }, (_, i) => at(i));
  const answer = at(visible);

  // Build distractors that are clearly different from the answer.
  const distractors: Glyph[] = [];
  let guard = 0;
  while (distractors.length < 3 && guard++ < 50) {
    let d: Glyph;
    if (rule === "rotate") d = { ...answer, rotation: sample([0, 45, 90, 135, 180, 225, 270, 315]) };
    else if (rule === "color") d = { ...answer, color: sample(PALETTE) };
    else d = { ...answer, scale: +(0.5 + Math.random() * 1.4).toFixed(2) };
    if (!glyphsEqual(d, answer) && !distractors.some((x) => glyphsEqual(x, d))) distractors.push(d);
  }

  const options = shuffle([answer, ...distractors]);
  const answerIndex = options.findIndex((o) => glyphsEqual(o, answer));
  return { sequence, options, answerIndex };
}

const _patDedup = makeDedup(16);
export function genPatternNext(level: number): PatternData {
  return _patDedup(
    () => _genPatternNext(level),
    (d) =>
      `${glyphSig(d.sequence[0])}>${glyphSig(d.sequence[d.sequence.length - 1])}>${glyphSig(d.options[d.answerIndex])}`,
  );
}

// ---- Count the Shapes -------------------------------------------------------
export interface CountData {
  cols: number;
  cells: Glyph[];
  targetShape: ShapeName;
  answer: number; // how many of targetShape are present
  options: number[]; // answer + plausible distractors
}

function _genCountShapes(level: number): CountData {
  const cols = level >= 5 ? 5 : 4;
  const rows = level >= 3 ? 4 : 3;
  const total = cols * rows;
  const targetShape = sample(SHAPES);

  // Choose a target count that's a real subset (never 0, never all of them),
  // scaling up a touch with level so it stays interesting.
  const minCount = 2;
  const maxCount = Math.min(total - 2, 3 + Math.floor(level / 2));
  const answer = minCount + randInt(Math.max(1, maxCount - minCount + 1));

  // Fill: `answer` target shapes, the rest from the other shapes.
  const others = SHAPES.filter((s) => s !== targetShape);
  const cells: Glyph[] = [];
  for (let i = 0; i < answer; i++) {
    cells.push({ shape: targetShape, color: sample(PALETTE), rotation: 0, scale: 1 });
  }
  for (let i = answer; i < total; i++) {
    cells.push({ shape: sample(others), color: sample(PALETTE), rotation: 0, scale: 1 });
  }
  const grid = shuffle(cells);

  // Four numeric options around the true count, all within [1, total].
  const opts = new Set<number>([answer]);
  let guard = 0;
  while (opts.size < 4 && guard++ < 60) {
    const delta = (randInt(3) + 1) * (Math.random() < 0.5 ? -1 : 1);
    const cand = answer + delta;
    if (cand >= 1 && cand <= total) opts.add(cand);
  }
  let extra = answer + 1;
  while (opts.size < 4) {
    if (extra <= total) opts.add(extra);
    extra++;
    if (extra > total + 4) break;
  }

  return {
    cols,
    cells: grid,
    targetShape,
    answer,
    options: shuffle([...opts]),
  };
}

const _countDedup = makeDedup(12);
export function genCountShapes(level: number): CountData {
  return _countDedup(
    () => _genCountShapes(level),
    (d) => `${d.cols}:${d.targetShape}:${d.answer}:${d.cells.map((c) => c.shape[0]).join("")}`,
  );
}

// ---- Find the Twin ----------------------------------------------------------
export interface MatchData {
  cols: number;
  target: Glyph;
  cells: Glyph[];
  matchIndex: number; // the one cell that exactly equals target
}

function _genFindMatch(level: number): MatchData {
  const cols = level >= 5 ? 4 : 3;
  const rows = level >= 3 ? 3 : 2;
  const total = cols * rows;
  const target = randomGlyph();

  const cells: Glyph[] = [];
  const matchIndex = randInt(total);
  let guard = 0;
  for (let i = 0; i < total; i++) {
    if (i === matchIndex) {
      cells.push({ ...target });
      continue;
    }
    // Build a distractor that is NOT an exact twin of the target.
    let d: Glyph;
    do {
      d = randomGlyph();
      // Rotation is invisible on a circle, so a circle distractor differing only
      // by rotation would look identical to a circle target — disallow that.
      if (target.shape === "circle" && d.shape === "circle" && d.color === target.color) {
        d = { ...d, color: sample(PALETTE.filter((c) => c !== target.color)) };
      }
    } while (
      (glyphsEqual(d, target) ||
        (target.shape === "circle" && d.shape === "circle" && d.color === target.color)) &&
      guard++ < 50
    );
    cells.push(d);
  }

  return { cols, target, cells, matchIndex };
}

const _matchDedup = makeDedup(12);
export function genFindMatch(level: number): MatchData {
  return _matchDedup(
    () => _genFindMatch(level),
    (d) => `${d.cols}:${glyphSig(d.target)}:${d.matchIndex}:${d.cells.map(glyphSig).join("|")}`,
  );
}
