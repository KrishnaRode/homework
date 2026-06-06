/* =============================================================================
 *  File:        frontend/components/Brand.tsx
 *  Description: Open-book logo, animated PrepWell wordmark, and a playful mascot
 *               that jumps out from behind the logo to play around it.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import Link from "next/link";
import { appConfig } from "@/app.config";

// The logo mark: a friendly open book on a rounded gradient tile. Pure SVG, so it
// stays crisp at any size and needs no image/network. `size` scales the whole mark.
export function Logo({ size = 46 }: { size?: number }) {
  const inner = Math.round(size * 0.64);
  return (
    <span
      className="brand-tile inline-grid place-items-center rounded-2xl bg-gradient-to-br from-accent to-accent-soft"
      style={{ width: size, height: size }}
    >
      <svg width={inner} height={inner} viewBox="0 0 48 48" fill="none" aria-hidden>
        {/* soft page shadow under the book */}
        <ellipse cx="24" cy="39.5" rx="15" ry="2.2" fill="#000" opacity="0.12" />
        {/* left page */}
        <path
          d="M24 12.5 C 18.5 9.3, 12 8.6, 6.8 10.6 C 6.2 10.8, 5.8 11.4, 5.8 12 L 5.8 33.6 C 5.8 34.4, 6.6 35, 7.4 34.8 C 12.2 33.3, 18.6 34, 24 36.8 Z"
          fill="#ffffff"
        />
        {/* right page */}
        <path
          d="M24 12.5 C 29.5 9.3, 36 8.6, 41.2 10.6 C 41.8 10.8, 42.2 11.4, 42.2 12 L 42.2 33.6 C 42.2 34.4, 41.4 35, 40.6 34.8 C 35.8 33.3, 29.4 34, 24 36.8 Z"
          fill="#ffffff"
          opacity="0.92"
        />
        {/* spine */}
        <path d="M24 12.5 L 24 36.8" stroke="var(--accent)" strokeWidth="1.6" strokeLinecap="round" opacity="0.55" />
        {/* ruled text lines — left page */}
        <path d="M10 17 q6 -1.4 10.5 0.7" stroke="var(--accent)" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.32" />
        <path d="M9.6 22 q6.4 -1.3 11 0.8" stroke="var(--accent)" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.32" />
        <path d="M9.6 27 q6.4 -1.2 11 0.8" stroke="var(--accent)" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.32" />
        {/* ruled text lines — right page */}
        <path d="M38 17 q-6 -1.4 -10.5 0.7" stroke="var(--accent)" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.32" />
        <path d="M38.4 22 q-6.4 -1.3 -11 0.8" stroke="var(--accent)" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.32" />
        <path d="M38.4 27 q-6.4 -1.2 -11 0.8" stroke="var(--accent)" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.32" />
        {/* little knowledge spark rising from the book */}
        <path
          d="M24 7.2 l1 2.2 2.2 1 -2.2 1 -1 2.2 -1 -2.2 -2.2 -1 2.2 -1 Z"
          fill="var(--joy-yellow)"
        />
      </svg>
    </span>
  );
}

// A tiny study-buddy robot. At rest it peeks from behind the logo; on a timer (and
// on hover) it JUMPS out in front and hops around the logo, then ducks back.
// Pure SVG + CSS (see globals.css .brand-* rules) — no JS, no images, no network.
function Mascot() {
  return (
    <span className="brand-stage" aria-hidden>
      <svg className="brand-buddy" viewBox="0 0 48 48" fill="none">
        <defs>
          <linearGradient id="prepMascot" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="var(--joy-purple)" />
            <stop offset="1" stopColor="var(--joy-blue)" />
          </linearGradient>
        </defs>
        {/* antenna */}
        <line x1="24" y1="13" x2="24" y2="7" stroke="url(#prepMascot)" strokeWidth="2.4" strokeLinecap="round" />
        <circle cx="24" cy="6" r="2.6" fill="var(--joy-yellow)" />
        {/* waving arms */}
        <line x1="11" y1="30" x2="5" y2="24" stroke="url(#prepMascot)" strokeWidth="2.6" strokeLinecap="round" />
        <line x1="37" y1="30" x2="43" y2="24" stroke="url(#prepMascot)" strokeWidth="2.6" strokeLinecap="round" />
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
      <Link href="/" className="brand group flex items-center gap-3">
        <span className="brand-logo-wrap">
          <Mascot />
          <Logo />
        </span>
        <span className="brand-word text-2xl font-extrabold tracking-tight">{appConfig.name}</span>
      </Link>
      <div className="flex items-center gap-2">{right}</div>
    </header>
  );
}
