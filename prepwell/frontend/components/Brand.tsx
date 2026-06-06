import Link from "next/link";
import { appConfig } from "@/app.config";

export function Logo({ size = 30 }: { size?: number }) {
  return (
    <span
      className="brand-tile inline-grid place-items-center rounded-xl bg-gradient-to-br from-accent to-accent-soft font-bold text-white"
      style={{ width: size, height: size, fontSize: size * 0.5 }}
    >
      P
    </span>
  );
}

// A tiny study-buddy mascot that peeks out from behind the logo and ducks back.
// Pure SVG + CSS (see globals.css .brand-* rules) — no JS, no images, no network.
function Mascot() {
  return (
    <span className="brand-stage" aria-hidden>
      <svg className="brand-peek" viewBox="0 0 48 48" fill="none">
        <defs>
          <linearGradient id="prepMascot" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="var(--joy-purple)" />
            <stop offset="1" stopColor="var(--joy-blue)" />
          </linearGradient>
        </defs>
        {/* antenna */}
        <line x1="24" y1="13" x2="24" y2="7" stroke="url(#prepMascot)" strokeWidth="2.4" strokeLinecap="round" />
        <circle cx="24" cy="6" r="2.6" fill="var(--joy-yellow)" />
        {/* body */}
        <circle cx="24" cy="30" r="15" fill="url(#prepMascot)" />
        {/* cheeks */}
        <circle cx="15" cy="32" r="2.3" fill="#ff8fbf" opacity="0.6" />
        <circle cx="33" cy="32" r="2.3" fill="#ff8fbf" opacity="0.6" />
        {/* eyes (blink together) */}
        <g className="brand-eyes">
          <ellipse cx="18.5" cy="26" rx="4.4" ry="4.8" fill="#fff" />
          <ellipse cx="29.5" cy="26" rx="4.4" ry="4.8" fill="#fff" />
          <circle cx="19.4" cy="27" r="2.1" fill="#241a4d" />
          <circle cx="30.4" cy="27" r="2.1" fill="#241a4d" />
          <circle cx="18.4" cy="25.8" r="0.8" fill="#fff" />
          <circle cx="29.4" cy="25.8" r="0.8" fill="#fff" />
        </g>
        {/* smile */}
        <path d="M20 34 q4 3.6 8 0" stroke="#241a4d" strokeWidth="1.7" fill="none" strokeLinecap="round" />
      </svg>
    </span>
  );
}

export function SeriesChip() {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-border bg-panel px-3 py-1 text-xs text-text-muted">
      <span className="h-1.5 w-1.5 rounded-full bg-accent" />
      {appConfig.series}
    </span>
  );
}

export function BrandHeader({ right }: { right?: React.ReactNode }) {
  return (
    <header className="mx-auto flex w-full max-w-[1000px] items-center justify-between px-5 py-5">
      <Link href="/" className="brand group flex items-center gap-2.5">
        <span className="brand-logo-wrap">
          <Mascot />
          <Logo />
        </span>
        <span className="brand-word text-lg font-semibold tracking-tight">{appConfig.name}</span>
      </Link>
      <div className="flex items-center gap-2">{right}</div>
    </header>
  );
}
