"use client";

import type { Evaluation } from "@/lib/types";

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1 text-xs uppercase tracking-wide text-text-faint">{label}</div>
      <div className="text-text-muted">{children}</div>
    </div>
  );
}

export default function AnswerView({
  evaluation,
  onNext,
  onStop,
}: {
  evaluation: Evaluation;
  onNext: () => void;
  onStop: () => void;
}) {
  const good = evaluation.correct;
  return (
    <div className="card animate-rise overflow-hidden">
      <div
        className={`flex items-center justify-between border-b border-border px-6 py-4 ${
          good ? "bg-good/10" : "bg-bad/10"
        }`}
      >
        <div className="flex items-center gap-3">
          <span className={`text-2xl ${good ? "text-good" : "text-bad"}`}>{good ? "✓" : "✕"}</span>
          <div>
            <div className="font-semibold">{good ? "Correct!" : "Not quite — let's learn it"}</div>
            <div className="text-sm text-text-muted">Score: {evaluation.score} / 100</div>
          </div>
        </div>
        <div className="text-right text-xs text-text-faint">
          Next difficulty<br />
          <span className="text-text">Level {evaluation.next_difficulty}</span>
        </div>
      </div>

      <div className="space-y-5 p-6">
        {evaluation.encouragement && (
          <p className="text-balance text-base font-medium text-text">{evaluation.encouragement}</p>
        )}

        {evaluation.what_was_right && (
          <Section label="What you got right">{evaluation.what_was_right}</Section>
        )}
        {evaluation.what_was_wrong && (
          <Section label="What to fix">{evaluation.what_was_wrong}</Section>
        )}
        {!good && evaluation.expected_answer && (
          <Section label="Correct answer">
            <span className="text-text">{evaluation.expected_answer}</span>
          </Section>
        )}

        {evaluation.step_by_step.length > 0 && (
          <Section label="Step by step">
            <ol className="list-decimal space-y-1 pl-5">
              {evaluation.step_by_step.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ol>
          </Section>
        )}

        {evaluation.how_to_think && (
          <div className="rounded-xl border border-accent-soft/30 bg-accent-soft/10 p-4">
            <div className="mb-1 text-xs uppercase tracking-wide text-accent">How to think 💡</div>
            <div className="text-text">{evaluation.how_to_think}</div>
          </div>
        )}

        {evaluation.misconception && (
          <Section label="Watch out for">{evaluation.misconception}</Section>
        )}

        <div className="flex gap-3 pt-1">
          <button
            onClick={onNext}
            className="flex-1 rounded-xl bg-accent px-5 py-3 font-semibold text-white transition hover:opacity-95 active:scale-[0.99]"
          >
            Next question →
          </button>
          <button
            onClick={onStop}
            className="rounded-xl border border-border bg-panel px-5 py-3 font-medium text-text-muted transition hover:bg-panel-hover hover:text-text active:scale-[0.99]"
          >
            Finish session
          </button>
        </div>
      </div>
    </div>
  );
}
