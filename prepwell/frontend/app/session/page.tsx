"use client";
/* =============================================================================
 *  File:        frontend/app/session/page.tsx
 *  Description: Practice session flow: question, answer, and adaptive loading.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import AnswerView from "@/components/AnswerView";
import { BrandHeader } from "@/components/Brand";
import LoadingState from "@/components/LoadingState";
import QuestionCard from "@/components/QuestionCard";
import ThemeToggle from "@/components/ThemeToggle";
import { api, ApiError } from "@/lib/api";
import { getSession } from "@/lib/auth";
import type { Evaluation, Question, SessionSummary } from "@/lib/types";

type Phase = "starting" | "loading" | "question" | "evaluating" | "answer" | "summary" | "error";

// A next question prefetched in the background. Never rejects — both outcomes are
// captured so a pending prefetch can be awaited safely when the student hits "Next".
type Prefetch = { q?: Question; err?: unknown };

function SessionInner() {
  const router = useRouter();
  const params = useSearchParams();
  const subject = params.get("subject") || "Maths";
  const topic = params.get("topic") || undefined;
  const adaptive = params.get("adaptive") === "1";

  const [phase, setPhase] = useState<Phase>("starting");
  const [sessionId, setSessionId] = useState<string>("");
  const [question, setQuestion] = useState<Question | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [error, setError] = useState("");
  const [stats, setStats] = useState({ answered: 0, correct: 0 });
  const started = useRef(false);
  const prefetch = useRef<Promise<Prefetch> | null>(null);

  const fetchNext = useCallback(
    (sid: string) => api.post<Question>("/api/session/next", { session_id: sid }),
    [],
  );

  const loadQuestion = useCallback(
    async (sid: string) => {
      setPhase("loading");
      setEvaluation(null);
      // Prefer a question already prefetched during the answer screen; otherwise
      // fetch one now. Either way, LoadingState keeps the brain quizzes looping
      // until this resolves.
      const pending = prefetch.current;
      prefetch.current = null;
      try {
        let q: Question;
        if (pending) {
          const r = await pending;
          if (r.err) throw r.err;
          q = r.q as Question;
        } else {
          q = await fetchNext(sid);
        }
        setQuestion(q);
        setPhase("question");
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Could not load the next question.");
        setPhase("error");
      }
    },
    [fetchNext],
  );

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    const s = getSession();
    if (!s || s.role !== "student") {
      router.replace("/login");
      return;
    }
    (async () => {
      try {
        const res = await api.post<{ session_id: string }>("/api/session/start", {
          subject,
          topic,
          adaptive,
        });
        setSessionId(res.session_id);
        await loadQuestion(res.session_id);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Could not start the session.");
        setPhase("error");
      }
    })();
  }, [router, subject, topic, adaptive, loadQuestion]);

  async function submitAnswer(answer: string, timeTaken: number) {
    if (!question) return;
    setPhase("evaluating");
    try {
      const ev = await api.post<Evaluation>("/api/session/answer", {
        session_id: sessionId,
        question_id: question.question_id,
        answer,
        time_taken_seconds: timeTaken,
      });
      setEvaluation(ev);
      setStats((s) => ({ answered: s.answered + 1, correct: s.correct + (ev.correct ? 1 : 0) }));
      setPhase("answer");
      // Generate the next question in the background while the student reads this
      // explanation, so it's often ready the moment they hit "Next". /answer has
      // already updated the mental model, so this stays fully adaptive.
      prefetch.current = fetchNext(sessionId).then(
        (q): Prefetch => ({ q }),
        (err): Prefetch => ({ err }),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not evaluate your answer.");
      setPhase("error");
    }
  }

  async function finish() {
    try {
      const sum = await api.post<SessionSummary>("/api/session/stop", { session_id: sessionId });
      setSummary(sum);
      setPhase("summary");
    } catch {
      router.push("/dashboard");
    }
  }

  const progress = question ? Math.min(100, (question.index / Math.min(question.limit, 20)) * 100) : 0;

  return (
    <div className="min-h-screen">
      <BrandHeader
        right={
          <>
            <ThemeToggle />
            <button
              onClick={() => router.push("/dashboard")}
              className="rounded-lg border border-border bg-panel px-3 py-1.5 text-sm text-text-muted transition hover:bg-panel-hover hover:text-text"
            >
              Exit
            </button>
          </>
        }
      />

      <main className="mx-auto max-w-[720px] px-5 pt-4">
        {phase !== "summary" && (
          <div className="mb-6">
            <div className="mb-2 flex justify-between text-sm text-text-muted">
              <span>{adaptive ? "Adaptive session" : `${subject}`}</span>
              <span>
                {stats.correct}/{stats.answered} correct
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-panel">
              <div
                className="h-full bg-gradient-to-r from-accent to-accent-soft transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {(phase === "starting" || phase === "loading" || phase === "evaluating") && (
          <LoadingState first={phase === "starting"} />
        )}

        {phase === "question" && question && (
          <QuestionCard question={question} onSubmit={submitAnswer} />
        )}

        {phase === "answer" && evaluation && (
          <AnswerView
            evaluation={evaluation}
            onNext={() => loadQuestion(sessionId)}
            onStop={finish}
          />
        )}

        {phase === "summary" && summary && (
          <SummaryCard summary={summary} stats={stats} onAgain={() => router.push("/dashboard")} />
        )}

        {phase === "error" && (
          <div className="card animate-rise p-6">
            <div className="text-lg font-semibold text-bad">Something interrupted the session</div>
            <p className="mt-2 text-text-muted">{error}</p>
            <div className="mt-5 flex gap-3">
              <button
                onClick={() => (sessionId ? loadQuestion(sessionId) : router.push("/dashboard"))}
                className="rounded-xl bg-accent px-5 py-2.5 font-semibold text-white"
              >
                Retry
              </button>
              <button
                onClick={() => router.push("/dashboard")}
                className="rounded-xl border border-border bg-panel px-5 py-2.5 text-text-muted"
              >
                Back to dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function SummaryCard({
  summary,
  stats,
  onAgain,
}: {
  summary: SessionSummary;
  stats: { answered: number; correct: number };
  onAgain: () => void;
}) {
  return (
    <div className="card animate-rise p-7 text-center">
      <div className="text-4xl">🎉</div>
      <h2 className="mt-3 text-2xl font-bold">Session complete!</h2>
      <p className="mt-1 text-text-muted">
        You answered {stats.answered} question{stats.answered === 1 ? "" : "s"} ·{" "}
        {summary.accuracy}% accuracy
      </p>

      <div className="mx-auto mt-6 grid max-w-sm grid-cols-3 gap-3">
        <Stat label="Answered" value={String(summary.total_questions)} />
        <Stat label="Correct" value={String(summary.correct)} />
        <Stat label="Learning index" value={String(summary.overall_index)} />
      </div>

      <div className="mt-6 space-y-4 text-left">
        {summary.strengths.length > 0 && (
          <Block title="Strengths 💪" items={summary.strengths} />
        )}
        {summary.weak_areas.length > 0 && (
          <Block title="Focus next 🎯" items={summary.weak_areas} />
        )}
      </div>

      <div className="mt-7 flex justify-center gap-3">
        <a
          href="/report"
          className="rounded-xl border border-border bg-panel px-5 py-2.5 font-medium text-text-muted transition hover:bg-panel-hover hover:text-text"
        >
          View full report
        </a>
        <button
          onClick={onAgain}
          className="rounded-xl bg-accent px-5 py-2.5 font-semibold text-white transition hover:opacity-95"
        >
          Practice again
        </button>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border-soft bg-bg-soft p-4">
      <div className="text-2xl font-bold text-accent">{value}</div>
      <div className="text-xs text-text-faint">{label}</div>
    </div>
  );
}

function Block({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl border border-border-soft bg-bg-soft p-4">
      <div className="mb-1.5 text-sm font-medium">{title}</div>
      <div className="flex flex-wrap gap-1.5">
        {items.map((x) => (
          <span key={x} className="rounded-full border border-border px-2.5 py-1 text-xs text-text-muted">
            {x}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function SessionPage() {
  return (
    <Suspense fallback={<div className="grid min-h-screen place-items-center text-text-muted">Loading…</div>}>
      <SessionInner />
    </Suspense>
  );
}
