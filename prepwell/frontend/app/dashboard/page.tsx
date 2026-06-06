"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { BrandHeader } from "@/components/Brand";
import ThemeToggle from "@/components/ThemeToggle";
import { api } from "@/lib/api";
import { clearSession, getSession } from "@/lib/auth";
import type { Session, Topic } from "@/lib/types";

const SUBJECT_ICON: Record<string, string> = { Maths: "➗", Science: "🔬", English: "✍️" };
const SUBJECT_COLOR: Record<string, string> = {
  Maths: "var(--joy-blue)",
  Science: "var(--joy-green)",
  English: "var(--joy-red)",
};
// Cycled across topic cards so the grid flaunts a rainbow of colours.
const TINTS = [
  "var(--joy-blue)",
  "var(--joy-green)",
  "var(--joy-red)",
  "var(--joy-yellow)",
  "var(--joy-purple)",
  "var(--joy-teal)",
  "var(--joy-orange)",
  "var(--joy-pink)",
];

export default function Dashboard() {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [subjects, setSubjects] = useState<string[]>([]);
  const [subject, setSubject] = useState<string>("");
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const s = getSession();
    if (!s || s.role !== "student") {
      router.replace("/login");
      return;
    }
    setSession(s);
    const board = s.board || "cbse";
    api
      .get<{ subjects: string[] }>(`/api/syllabus/subjects?class=${s.klass}&board=${board}`)
      .then((r) => {
        setSubjects(r.subjects);
        if (r.subjects[0]) setSubject(r.subjects[0]);
      })
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!session || !subject) return;
    const board = session.board || "cbse";
    api
      .get<{ topics: Topic[] }>(`/api/syllabus/topics?class=${session.klass}&subject=${subject}&board=${board}`)
      .then((r) => setTopics(r.topics));
  }, [session, subject]);

  function start(topicId?: string) {
    const params = new URLSearchParams({ subject });
    if (topicId) params.set("topic", topicId);
    else params.set("adaptive", "1");
    router.push(`/session?${params.toString()}`);
  }

  function logout() {
    clearSession();
    router.push("/");
  }

  if (loading || !session) {
    return <div className="grid min-h-screen place-items-center text-text-muted">Loading…</div>;
  }

  return (
    <div className="min-h-screen">
      <BrandHeader
        right={
          <>
            <ThemeToggle />
            <button
              onClick={logout}
              className="rounded-lg border border-border bg-panel px-3 py-1.5 text-sm text-text-muted transition hover:bg-panel-hover hover:text-text"
            >
              Log out
            </button>
          </>
        }
      />

      <main className="mx-auto max-w-[900px] px-5 pt-8">
        <h1 className="text-3xl font-bold tracking-tight">
          Hi {session.name} 👋
        </h1>
        <p className="mt-1.5 text-text-muted">
          Class {session.klass}
          {session.board ? ` · ${session.board.toUpperCase()}` : ""}. Pick a subject and topic, or let
          PrepWell choose what you need most.
        </p>

        <a
          href="/games"
          className="card-pop mt-6 flex items-center justify-between px-6 py-4 transition hover:-translate-y-0.5 active:scale-[0.99]"
          style={{ ["--tint"]: "var(--joy-purple)" } as React.CSSProperties}
        >
          <div>
            <div className="font-semibold">🧠 Brain Games</div>
            <div className="text-sm text-text-muted">
              Quick reasoning puzzles — separate from your learning score.
            </div>
          </div>
          <span className="text-2xl" style={{ color: "var(--joy-purple)" }}>
            →
          </span>
        </a>

        {subjects.length === 0 ? (
          <div className="card mt-8 p-6 text-center">
            <div className="text-3xl">📚</div>
            <h2 className="mt-2 text-lg font-semibold">No syllabus for your class yet</h2>
            <p className="mx-auto mt-1.5 max-w-md text-sm text-text-muted">
              We don&apos;t have practice topics for Class {session.klass}
              {session.board ? ` (${session.board.toUpperCase()})` : ""} right now. Your teacher can
              add them, or you can still warm up with{" "}
              <a href="/games" className="text-accent hover:underline">
                Brain Games
              </a>
              .
            </p>
          </div>
        ) : (
          <>
        <div className="mt-8 flex flex-wrap gap-2">
          {subjects.map((s) => {
            const color = SUBJECT_COLOR[s] || "var(--accent)";
            const active = subject === s;
            return (
              <button
                key={s}
                onClick={() => setSubject(s)}
                style={
                  active
                    ? {
                        borderColor: color,
                        background: `color-mix(in srgb, ${color} 16%, transparent)`,
                        color: "var(--text)",
                      }
                    : undefined
                }
                className={`rounded-xl border px-5 py-3 font-medium transition active:scale-95 ${
                  active ? "" : "border-border bg-panel text-text-muted hover:bg-panel-hover"
                }`}
              >
                <span className="mr-2">{SUBJECT_ICON[s]}</span>
                {s}
              </button>
            );
          })}
        </div>

        <button
          onClick={() => start()}
          className="mt-6 flex w-full items-center justify-between rounded-2xl px-6 py-5 text-left text-white shadow-lg transition hover:opacity-95 hover:-translate-y-0.5 active:scale-[0.99]"
          style={{
            background:
              "linear-gradient(100deg, var(--joy-purple), var(--accent) 40%, var(--joy-blue) 75%, var(--joy-teal))",
          }}
        >
          <div>
            <div className="text-lg font-semibold">⚡ Start Adaptive Session</div>
            <div className="text-sm text-white/85">
              PrepWell picks your weakest topics and adjusts difficulty as you go.
            </div>
          </div>
          <span className="text-2xl">→</span>
        </button>

        <h2 className="mb-3 mt-10 text-sm uppercase tracking-wide text-text-faint">
          Or choose a {subject} topic
        </h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {topics.map((t, i) => {
            const tint = TINTS[i % TINTS.length];
            return (
              <button
                key={t.topic_id}
                onClick={() => start(t.topic_id)}
                style={{ ["--tint"]: tint } as React.CSSProperties}
                className="card-pop p-5 text-left transition hover:-translate-y-0.5 active:scale-[0.99]"
              >
                <div
                  className="text-xs font-semibold uppercase tracking-wide"
                  style={{ color: tint }}
                >
                  {t.chapter_title}
                </div>
                <div className="mt-0.5 font-semibold">{t.title}</div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {t.skills.slice(0, 3).map((sk) => (
                    <span
                      key={sk}
                      className="rounded-full px-2 py-0.5 text-xs"
                      style={{
                        background: `color-mix(in srgb, ${tint} 16%, transparent)`,
                        color: "var(--text-muted)",
                      }}
                    >
                      {sk}
                    </span>
                  ))}
                </div>
              </button>
            );
          })}
        </div>
          </>
        )}

        <div className="mt-10">
          <a href="/report" className="text-sm text-accent hover:underline">
            View my progress report →
          </a>
        </div>
      </main>
    </div>
  );
}
