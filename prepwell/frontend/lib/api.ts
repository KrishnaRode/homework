"use client";
/* =============================================================================
 *  File:        frontend/lib/api.ts
 *  Description: Typed fetch wrapper for the backend API.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import { clearSession, getSession } from "./auth";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// A request fails authentication when the token is missing/expired (401), or when
// the logged-in student's account no longer exists (404 "Student not found"). In
// either case the stored session is dead — clear it and send the user to login.
// The student-role guard keeps admins (who may legitimately get a 404 viewing a
// deleted student) signed in.
function isAuthFailure(status: number, detail: string): boolean {
  if (status === 401) return true;
  if (status === 404 && /student not found/i.test(detail)) {
    return getSession()?.role === "student";
  }
  return false;
}

function handleAuthFailure() {
  clearSession();
  if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
    window.location.href = "/login";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (auth) {
    const s = getSession();
    if (s?.token) headers["Authorization"] = `Bearer ${s.token}`;
  }
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, "Cannot reach the PrepWell backend. Is it running on port 8000?");
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    if (isAuthFailure(res.status, detail)) {
      handleAuthFailure();
      throw new ApiError(res.status, "Your session has ended. Please log in again.");
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(p: string, auth = true) => request<T>(p, { method: "GET" }, auth),
  post: <T>(p: string, body?: unknown, auth = true) =>
    request<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined }, auth),
  patch: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  del: <T>(p: string) => request<T>(p, { method: "DELETE" }),
};
