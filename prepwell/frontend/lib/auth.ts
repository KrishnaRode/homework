"use client";
/* =============================================================================
 *  File:        frontend/lib/auth.ts
 *  Description: Client-side session helpers (read/store the logged-in user).
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
import type { Session } from "./types";

const KEY = "prepwell_session";

export function saveSession(s: Session) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, JSON.stringify(s));
}

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}

export function clearSession() {
  if (typeof window !== "undefined") localStorage.removeItem(KEY);
}
