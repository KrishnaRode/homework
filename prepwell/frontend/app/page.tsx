import Link from "next/link";
import { appConfig } from "@/app.config";
import { BrandHeader, SeriesChip } from "@/components/Brand";
import ThemeToggle from "@/components/ThemeToggle";

const FEATURES = [
  {
    title: "Adaptive questions",
    body: "Every question is generated for you — the right topic, type, and difficulty based on how you're doing.",
    icon: "🎯",
    tint: "var(--joy-pink)",
  },
  {
    title: "It builds a mental model of you",
    body: "PrepWell tracks your accuracy, speed, confidence and reasoning, then plans what to practice next.",
    icon: "🧠",
    tint: "var(--joy-blue)",
  },
  {
    title: "It teaches you how to think",
    body: "Not just right/wrong — every answer explains the strategy and the common mistake to avoid.",
    icon: "💡",
    tint: "var(--joy-yellow)",
  },
  {
    title: "100% local & private",
    body: "Runs on your laptop with free local AI. No cloud, no accounts to the internet, no data leaves your device.",
    icon: "🔒",
    tint: "var(--joy-teal)",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      <BrandHeader
        right={
          <>
            <ThemeToggle />
            <Link
              href="/login"
              className="rounded-lg bg-accent px-4 py-1.5 text-sm font-medium text-white transition hover:opacity-95 active:scale-95"
            >
              Log in
            </Link>
          </>
        }
      />

      <main className="mx-auto max-w-[900px] px-5">
        <section className="flex flex-col items-center pt-16 text-center">
          <SeriesChip />
          <h1 className="mt-6 text-balance text-5xl font-extrabold tracking-tight sm:text-6xl">
            <span className="bg-gradient-to-r from-accent via-joy-pink to-joy-teal bg-clip-text text-transparent">
              {appConfig.name}
            </span>
          </h1>
          <p className="mt-4 max-w-xl text-balance text-lg text-text-muted">
            {appConfig.tagline} A private AI tutor on your laptop that understands how every
            student learns — across Maths, Science and English.
          </p>
          <div className="mt-8 flex gap-3">
            <Link
              href="/login"
              className="rounded-xl bg-accent px-6 py-3 font-semibold text-white transition hover:opacity-95 active:scale-95"
            >
              Start practising
            </Link>
            <a
              href={appConfig.repoUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl border border-border bg-panel px-6 py-3 font-medium text-text-muted transition hover:bg-panel-hover hover:text-text"
            >
              View source
            </a>
          </div>
        </section>

        <section className="mt-20 grid gap-4 sm:grid-cols-2">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="card p-6 transition hover:-translate-y-1 hover:bg-panel-hover"
            >
              <div
                className="grid h-12 w-12 place-items-center rounded-2xl text-2xl"
                style={{ background: `color-mix(in srgb, ${f.tint} 22%, transparent)` }}
              >
                {f.icon}
              </div>
              <h3 className="mt-3 text-lg font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-text-muted">{f.body}</p>
            </div>
          ))}
        </section>

        <footer className="mt-20 border-t border-border-soft py-8 text-center text-sm text-text-faint">
          {appConfig.series} · PrepWell runs entirely on your device.
        </footer>
      </main>
    </div>
  );
}
