"use client";
/* =============================================================================
 *  File:        frontend/app/login/page.tsx
 *  Description: Login page for admin-created student and admin accounts.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { useRouter } from "next/navigation";
import { useState } from "react";
import { appConfig } from "@/app.config";
import { BrandHeader } from "@/components/Brand";
import ThemeToggle from "@/components/ThemeToggle";
import { api, ApiError } from "@/lib/api";
import { saveSession } from "@/lib/auth";
import type { Session } from "@/lib/types";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const s = await api.post<Session>("/api/auth/login", { username, password }, false);
      saveSession(s);
      router.push(s.role === "admin" ? "/admin" : "/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <BrandHeader right={<ThemeToggle />} />
      <main className="mx-auto flex max-w-[420px] flex-col px-5 pt-16">
        <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
        <p className="mt-2 text-text-muted">Log in to keep learning with {appConfig.name}.</p>

        <form onSubmit={submit} className="card mt-8 space-y-4 p-6">
          <div>
            <label className="mb-1.5 block text-sm text-text-muted">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              className="w-full rounded-xl border border-border bg-bg-soft px-4 py-2.5 outline-none transition focus:border-accent"
              placeholder="e.g. aarav"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm text-text-muted">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-border bg-bg-soft px-4 py-2.5 outline-none transition focus:border-accent"
              placeholder="••••••••"
            />
          </div>
          {error && (
            <div className="rounded-lg border border-bad/40 bg-bad/10 px-3.5 py-2.5 text-sm text-bad">
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={loading || !username || !password}
            className="w-full rounded-xl bg-accent px-5 py-3 font-semibold text-white transition hover:opacity-95 active:scale-[0.99] disabled:opacity-40"
          >
            {loading ? "Logging in…" : "Log in"}
          </button>
        </form>

        <div className="mt-5 rounded-xl border border-border-soft bg-bg-soft p-4 text-sm text-text-muted">
          <div className="mb-1 font-medium text-text">Demo logins</div>
          Student: <code className="text-accent">aarav / aarav123</code>
          <br />
          Admin: <code className="text-accent">admin / prepwell123</code>
        </div>
      </main>
    </div>
  );
}
