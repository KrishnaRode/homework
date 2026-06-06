"use client";
/* =============================================================================
 *  File:        frontend/app/report/page.tsx
 *  Description: Student progress report view.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { BrandHeader } from "@/components/Brand";
import ThemeToggle from "@/components/ThemeToggle";
import { api, API_BASE } from "@/lib/api";
import { getSession } from "@/lib/auth";

interface Summary {
  name: string;
  class: string;
  overall_index: number;
  accuracy_index: number;
  confidence_index: number;
  speed_index: number;
  reasoning_index: number;
  strengths: string[];
  weak_areas: string[];
  recommended_next_topics: string[];
  topic_mastery: Record<string, { title?: string; mastery: number; attempts: number; correct: number }>;
}

const BAR_TINTS = [
  "var(--joy-blue)",
  "var(--joy-green)",
  "var(--joy-orange)",
  "var(--joy-purple)",
  "var(--joy-pink)",
  "var(--joy-teal)",
  "var(--joy-red)",
  "var(--joy-yellow)",
];

function Bar({ label, value, tint = "var(--accent)" }: { label: string; value: number; tint?: string }) {
  return (
    <div className="flex items-center gap-3 py-1.5">
      <span className="w-28 text-sm text-text-muted">{label}</span>
      <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-bg-soft">
        <div
          className="h-full rounded-full"
          style={{
            width: `${value}%`,
            background: `linear-gradient(90deg, color-mix(in srgb, ${tint} 70%, transparent), ${tint})`,
          }}
        />
      </div>
      <span className="w-9 text-right text-sm font-semibold" style={{ color: tint }}>
        {value}
      </span>
    </div>
  );
}

export default function ReportPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const s = getSession();
    if (!s || s.role !== "student") {
      router.replace("/login");
      return;
    }
    api
      .get<{ summary: Summary }>("/api/me/progress")
      .then((r) => setSummary(r.summary))
      .catch(() => setError("Could not load your report."));
  }, [router]);

  async function downloadHtml() {
    const s = getSession();
    const res = await fetch(`${API_BASE}/api/me/report?format=html`, {
      headers: { Authorization: `Bearer ${s?.token}` },
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  }

  if (error) return <div className="grid min-h-screen place-items-center text-bad">{error}</div>;
  if (!summary) return <div className="grid min-h-screen place-items-center text-text-muted">Loading…</div>;

  const mastery = Object.entries(summary.topic_mastery);

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
              Dashboard
            </button>
          </>
        }
      />

      <main className="mx-auto max-w-[820px] px-5 pt-6">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">My progress</h1>
            <p className="mt-1 text-text-muted">{summary.name} · Class {summary.class}</p>
          </div>
          <button
            onClick={downloadHtml}
            className="rounded-xl border border-border bg-panel px-4 py-2 text-sm font-medium text-text-muted transition hover:bg-panel-hover hover:text-text"
          >
            Export HTML
          </button>
        </div>

        <div
          className="card-pop mt-6 p-6"
          style={{ ["--tint"]: "var(--joy-purple)" } as React.CSSProperties}
        >
          <div className="text-sm text-text-faint">Overall learning index</div>
          <div className="text-5xl font-extrabold" style={{ color: "var(--joy-purple)" }}>
            {summary.overall_index}
            <span className="text-2xl text-text-faint">/100</span>
          </div>
        </div>

        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div
            className="card-pop p-6"
            style={{ ["--tint"]: "var(--joy-blue)" } as React.CSSProperties}
          >
            <h3 className="mb-2 font-semibold">Learning indices</h3>
            <Bar label="Accuracy" value={summary.accuracy_index} tint="var(--joy-green)" />
            <Bar label="Confidence" value={summary.confidence_index} tint="var(--joy-yellow)" />
            <Bar label="Speed" value={summary.speed_index} tint="var(--joy-orange)" />
            <Bar label="Reasoning" value={summary.reasoning_index} tint="var(--joy-purple)" />
          </div>
          <div
            className="card-pop p-6"
            style={{ ["--tint"]: "var(--joy-green)" } as React.CSSProperties}
          >
            <h3 className="mb-2 font-semibold">Strengths & focus</h3>
            <div className="mb-1 text-xs uppercase tracking-wide text-text-faint">Strengths 💪</div>
            <div className="mb-3 flex flex-wrap gap-1.5">
              {summary.strengths.length ? (
                summary.strengths.map((x) => (
                  <span key={x} className="rounded-full border border-good/40 bg-good/10 px-2.5 py-1 text-xs text-good">
                    {x}
                  </span>
                ))
              ) : (
                <span className="text-sm text-text-faint">Building up…</span>
              )}
            </div>
            <div className="mb-1 text-xs uppercase tracking-wide text-text-faint">Focus next 🎯</div>
            <div className="flex flex-wrap gap-1.5">
              {summary.weak_areas.length ? (
                summary.weak_areas.map((x) => (
                  <span key={x} className="rounded-full border border-border px-2.5 py-1 text-xs text-text-muted">
                    {x}
                  </span>
                ))
              ) : (
                <span className="text-sm text-text-faint">None yet 🎉</span>
              )}
            </div>
          </div>
        </div>

        {mastery.length > 0 && (
          <div
            className="card-pop mt-4 p-6"
            style={{ ["--tint"]: "var(--joy-pink)" } as React.CSSProperties}
          >
            <h3 className="mb-3 font-semibold">Topic mastery</h3>
            {mastery.map(([key, tm], i) => (
              <Bar
                key={key}
                label={tm.title || key.split(".").pop() || key}
                value={tm.mastery}
                tint={BAR_TINTS[i % BAR_TINTS.length]}
              />
            ))}
          </div>
        )}

        <div className="py-10 text-center text-sm text-text-faint">
          Generated locally · No data leaves your device.
        </div>
      </main>
    </div>
  );
}
