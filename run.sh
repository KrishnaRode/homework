#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Sunday AI Template — one-command launcher (macOS / Linux)
#  Checks Node + Ollama, starts Ollama, pulls the model,
#  installs deps, then runs the app.
# ─────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

OLLAMA_HOST_URL="${OLLAMA_HOST:-http://localhost:11434}"

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
info() { printf "\033[36m›\033[0m %s\n" "$1"; }
ok()   { printf "\033[32m✓\033[0m %s\n" "$1"; }
err()  { printf "\033[31m✗ %s\033[0m\n" "$1" >&2; }

bold "Free AI. Real Problems. Every Sunday."
echo

# 1) Node.js + npm ------------------------------------------------------------
if ! command -v node >/dev/null 2>&1; then
  err "Node.js is not installed. Install the LTS version from https://nodejs.org"
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  err "npm is not installed (it ships with Node.js)."
  exit 1
fi
ok "Node.js $(node --version)"

# 2) Ollama -------------------------------------------------------------------
if ! command -v ollama >/dev/null 2>&1; then
  err "Ollama is not installed. Install it from https://ollama.com/download"
  exit 1
fi
ok "Ollama $(ollama --version 2>/dev/null | head -1)"

# 3) Resolve the model from app.config.ts (override with: MODEL=name ./run.sh)
MODEL="${MODEL:-$(grep -Eo 'defaultModel:[[:space:]]*"[^"]+"' app.config.ts 2>/dev/null | grep -Eo '"[^"]+"' | tail -1 | tr -d '"')}"
MODEL="${MODEL:-qwen2.5-coder}"
info "Model: ${MODEL}"

# 4) Make sure the Ollama server is up ---------------------------------------
if ! curl -fsS "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1; then
  info "Starting 'ollama serve' in the background…"
  ollama serve >/tmp/ollama-serve.log 2>&1 &
  for _ in $(seq 1 30); do
    curl -fsS "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1 && break
    sleep 1
  done
fi
if ! curl -fsS "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1; then
  err "Could not reach Ollama at ${OLLAMA_HOST_URL}. Try running 'ollama serve' manually."
  exit 1
fi
ok "Ollama is running"

# 5) Pull the model if it isn't present --------------------------------------
if ! ollama list 2>/dev/null | grep -qiF "${MODEL}"; then
  info "Pulling '${MODEL}' (first run only, this can take a few minutes)…"
  ollama pull "${MODEL}"
fi
ok "Model '${MODEL}' is ready"

# 6) Install dependencies -----------------------------------------------------
if [ ! -d node_modules ]; then
  info "Installing dependencies…"
  npm install
fi
ok "Dependencies installed"

# 7) Launch -------------------------------------------------------------------
echo
bold "Starting the app → http://localhost:3000"
echo
exec npm run dev
