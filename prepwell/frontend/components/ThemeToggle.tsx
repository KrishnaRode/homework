"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const saved = (localStorage.getItem("prepwell_theme") as "dark" | "light") || "dark";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("prepwell_theme", next);
    document.documentElement.setAttribute("data-theme", next);
  }

  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className="rounded-lg border border-border bg-panel px-3 py-1.5 text-sm text-text-muted transition hover:bg-panel-hover hover:text-text active:scale-95"
    >
      {theme === "dark" ? "☀ Light" : "☾ Dark"}
    </button>
  );
}
