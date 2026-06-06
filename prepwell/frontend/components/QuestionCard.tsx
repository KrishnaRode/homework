"use client";
/* =============================================================================
 *  File:        frontend/components/QuestionCard.tsx
 *  Description: Question renderer: passage, MCQ/text input, and submit.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useEffect, useState } from "react";
import type { Question } from "@/lib/types";

const TYPE_LABEL: Record<string, string> = {
  mcq: "Multiple choice",
  short_answer: "Short answer",
  explain: "Explain in your own words",
  fill_blank: "Fill in the blank",
  true_false_reason: "True / False + reason",
  diagram: "Diagram",
  step_problem: "Step-by-step problem",
  word_problem: "Word problem",
  reasoning: "Reasoning",
  match: "Match the following",
  spot_mistake: "Spot the mistake",
  improve_answer: "Improve the answer",
};

const DIFF = ["", "Very easy", "Easy", "Medium", "Hard", "Challenge"];

export default function QuestionCard({
  question,
  onSubmit,
  disabled,
}: {
  question: Question;
  onSubmit: (answer: string, timeTaken: number) => void;
  disabled?: boolean;
}) {
  const [answer, setAnswer] = useState("");
  const [start] = useState(() => Date.now());

  useEffect(() => {
    setAnswer("");
  }, [question.question_id]);

  function submit() {
    if (!answer.trim() || disabled) return;
    onSubmit(answer.trim(), Math.round((Date.now() - start) / 1000));
  }

  const isMcq = question.type === "mcq" && question.options.length > 0;

  return (
    <div className="card animate-rise p-6">
      <div className="mb-4 flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-accent-soft/20 px-2.5 py-1 font-medium text-accent">
          {question.subject}
        </span>
        <span className="rounded-full border border-border px-2.5 py-1 text-text-muted">
          {TYPE_LABEL[question.type] || question.type}
        </span>
        <span className="rounded-full border border-border px-2.5 py-1 text-text-muted">
          {DIFF[question.difficulty] || `Level ${question.difficulty}`}
        </span>
        <span className="ml-auto text-text-faint">
          Q{question.index} / {question.limit}
        </span>
      </div>

      {question.passage && (
        <div className="mb-5 rounded-xl border border-border-soft bg-bg-soft p-4">
          <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-wide text-text-faint">
            <span>📖 Read the passage</span>
            {question.set_total ? (
              <span>
                Question {question.set_index} of {question.set_total}
              </span>
            ) : null}
          </div>
          <p className="whitespace-pre-line text-[0.95rem] leading-relaxed text-text">
            {question.passage}
          </p>
        </div>
      )}

      <h2 className="text-balance text-xl font-semibold leading-snug">{question.question}</h2>

      <div className="mt-5">
        {isMcq ? (
          <div className="grid gap-2.5">
            {question.options.map((opt, i) => {
              const selected = answer === opt;
              return (
                <button
                  key={i}
                  disabled={disabled}
                  onClick={() => setAnswer(opt)}
                  className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition active:scale-[0.99] ${
                    selected
                      ? "border-accent bg-accent-soft/10"
                      : "border-border bg-bg-soft hover:bg-panel-hover"
                  }`}
                >
                  <span
                    className={`grid h-6 w-6 shrink-0 place-items-center rounded-md border text-xs ${
                      selected ? "border-accent text-accent" : "border-border text-text-faint"
                    }`}
                  >
                    {String.fromCharCode(65 + i)}
                  </span>
                  <span>{opt}</span>
                </button>
              );
            })}
          </div>
        ) : (
          <textarea
            value={answer}
            disabled={disabled}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === "Enter") submit();
            }}
            rows={4}
            placeholder="Type your answer here… (⌘/Ctrl + Enter to submit)"
            className="w-full resize-none rounded-xl border border-border bg-bg-soft p-4 text-text outline-none transition focus:border-accent"
          />
        )}
      </div>

      <button
        onClick={submit}
        disabled={!answer.trim() || disabled}
        className="mt-5 w-full rounded-xl bg-accent px-5 py-3 font-semibold text-white transition hover:opacity-95 active:scale-[0.99] disabled:opacity-40"
      >
        Submit answer
      </button>
    </div>
  );
}
