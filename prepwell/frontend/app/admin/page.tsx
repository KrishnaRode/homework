"use client";
/* =============================================================================
 *  File:        frontend/app/admin/page.tsx
 *  Description: Admin console: roster management and credential generation.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { BrandHeader } from "@/components/Brand";
import ThemeToggle from "@/components/ThemeToggle";
import { api, API_BASE } from "@/lib/api";
import { clearSession, getSession } from "@/lib/auth";
import type { Board, StudentRow } from "@/lib/types";

interface Syllabus {
  class: string;
  subject: string;
  chapters: { topics: unknown[] }[];
}

const CLASSES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];

export default function AdminPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"students" | "syllabus">("students");
  const [students, setStudents] = useState<StudentRow[]>([]);
  const [boards, setBoards] = useState<Board[]>([]);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [syllabusBoard, setSyllabusBoard] = useState("cbse");
  const [newCreds, setNewCreds] = useState<{ username: string; password: string } | null>(null);
  const [form, setForm] = useState({ name: "", class: "5", board: "cbse" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(() => {
    api.get<{ students: StudentRow[] }>("/api/admin/students").then((r) => setStudents(r.students));
    api.get<{ boards: Board[] }>("/api/admin/boards").then((r) => setBoards(r.boards));
  }, []);

  useEffect(() => {
    const s = getSession();
    if (!s || s.role !== "admin") {
      router.replace("/login");
      return;
    }
    refresh();
  }, [router, refresh]);

  useEffect(() => {
    api
      .get<{ syllabi: Syllabus[] }>(`/api/admin/syllabus?board=${syllabusBoard}`)
      .then((r) => setSyllabi(r.syllabi));
  }, [syllabusBoard]);

  async function createStudent(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await api.post<{ username: string; password: string }>("/api/admin/students", {
        name: form.name,
        class: form.class,
        board: form.board,
      });
      setNewCreds({ username: res.username, password: res.password });
      setForm({ name: "", class: form.class, board: form.board });
      refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create student");
    } finally {
      setBusy(false);
    }
  }

  async function resetStudent(id: string) {
    if (!confirm("Reset this student's history and mental model?")) return;
    await api.post(`/api/admin/students/${id}/reset`);
    refresh();
  }

  async function removeStudent(id: string) {
    if (!confirm("Delete this student permanently?")) return;
    await api.del(`/api/admin/students/${id}`);
    refresh();
  }

  async function openReport(id: string) {
    const s = getSession();
    const res = await fetch(`${API_BASE}/api/admin/students/${id}/report?format=html`, {
      headers: { Authorization: `Bearer ${s?.token}` },
    });
    const url = URL.createObjectURL(await res.blob());
    window.open(url, "_blank");
  }

  function logout() {
    clearSession();
    router.push("/");
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

      <main className="mx-auto max-w-[960px] px-5 pt-6">
        <h1 className="text-3xl font-bold tracking-tight">Admin</h1>
        <p className="mt-1 text-text-muted">Manage students and syllabus. Everything is stored locally.</p>

        <div className="mt-6 flex gap-2">
          {(["students", "syllabus"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`rounded-lg px-4 py-2 text-sm font-medium capitalize transition ${
                tab === t ? "bg-accent text-white" : "border border-border bg-panel text-text-muted hover:bg-panel-hover"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === "students" && (
          <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
            <div className="card overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-text-faint">
                    <th className="px-4 py-3 font-medium">Name</th>
                    <th className="px-4 py-3 font-medium">Username</th>
                    <th className="px-4 py-3 font-medium">Class</th>
                    <th className="px-4 py-3 font-medium">Board</th>
                    <th className="px-4 py-3 font-medium">Index</th>
                    <th className="px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.student_id} className="border-b border-border-soft last:border-0">
                      <td className="px-4 py-3 font-medium">{s.name}</td>
                      <td className="px-4 py-3 text-text-muted">{s.username}</td>
                      <td className="px-4 py-3 text-text-muted">{s.class}</td>
                      <td className="px-4 py-3 text-text-muted uppercase">{s.board}</td>
                      <td className="px-4 py-3">
                        <span className="rounded-full bg-accent-soft/15 px-2 py-0.5 text-xs text-accent">
                          {s.overall_index}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1.5 text-xs">
                          <button onClick={() => openReport(s.student_id)} className="text-accent hover:underline">
                            Report
                          </button>
                          <button onClick={() => resetStudent(s.student_id)} className="text-text-muted hover:underline">
                            Reset
                          </button>
                          <button onClick={() => removeStudent(s.student_id)} className="text-bad hover:underline">
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {students.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-text-faint">
                        No students yet — create one →
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="card h-fit p-5">
              <h3 className="font-semibold">Add a student</h3>
              <form onSubmit={createStudent} className="mt-4 space-y-3">
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Student name"
                  required
                  className="w-full rounded-lg border border-border bg-bg-soft px-3 py-2 outline-none focus:border-accent"
                />
                <select
                  value={form.class}
                  onChange={(e) => setForm({ ...form, class: e.target.value })}
                  className="w-full rounded-lg border border-border bg-bg-soft px-3 py-2 outline-none focus:border-accent"
                >
                  {CLASSES.map((c) => (
                    <option key={c} value={c}>
                      Class {c}
                    </option>
                  ))}
                </select>
                <select
                  value={form.board}
                  onChange={(e) => setForm({ ...form, board: e.target.value })}
                  className="w-full rounded-lg border border-border bg-bg-soft px-3 py-2 outline-none focus:border-accent"
                >
                  {boards.map((b) => (
                    <option key={b.code} value={b.code}>
                      {b.name}
                    </option>
                  ))}
                </select>
                <button
                  type="submit"
                  disabled={busy}
                  className="w-full rounded-lg bg-accent px-4 py-2.5 font-semibold text-white transition hover:opacity-95 disabled:opacity-40"
                >
                  {busy ? "Creating…" : "Create student"}
                </button>
              </form>
              {error && <p className="mt-3 text-sm text-bad">{error}</p>}
              {newCreds && (
                <div className="mt-4 rounded-lg border border-good/40 bg-good/10 p-3 text-sm">
                  <div className="font-medium text-text">Credentials (shown once):</div>
                  <div className="mt-1 text-text-muted">
                    User: <code className="text-accent">{newCreds.username}</code>
                    <br />
                    Pass: <code className="text-accent">{newCreds.password}</code>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {tab === "syllabus" && (
          <div className="mt-6">
            <div className="mb-4 flex items-center gap-2">
              <label className="text-sm text-text-muted">Board</label>
              <select
                value={syllabusBoard}
                onChange={(e) => setSyllabusBoard(e.target.value)}
                className="rounded-lg border border-border bg-bg-soft px-3 py-1.5 text-sm outline-none focus:border-accent"
              >
                {boards.map((b) => (
                  <option key={b.code} value={b.code}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {syllabi.map((s) => (
                <div key={`${s.class}-${s.subject}`} className="card p-5">
                  <div className="font-semibold">
                    Class {s.class} · {s.subject}
                  </div>
                  <div className="mt-1 text-sm text-text-muted">
                    {s.chapters.length} chapters ·{" "}
                    {s.chapters.reduce((n, c) => n + c.topics.length, 0)} topics
                  </div>
                </div>
              ))}
              <div className="card border-dashed p-5 text-sm text-text-faint">
                Curriculum is curated from the NCERT framework (classes 1–10) and shared across boards.
                Drop a <code>data/syllabus/&lt;board&gt;_class&lt;N&gt;_&lt;subject&gt;.json</code> file to
                specialise any board — no code change.
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
