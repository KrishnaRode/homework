#!/usr/bin/env bash
# =============================================================================
#  File:        run.sh
#  Description: One-command launcher: Ollama, FastAPI backend, and Next.js frontend.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
# ─────────────────────────────────────────────────────────────
#  PrepWell — one-command launcher (macOS / Linux)
#  Starts Ollama, the FastAPI backend, and the Next.js frontend.
# ─────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

OLLAMA_HOST_URL="${OLLAMA_HOST:-http://localhost:11434}"
MODEL="${PREPWELL_MODEL:-llama3.2:3b}"
BACKEND_PORT="${PREPWELL_PORT:-8000}"

info() { printf "\033[36m›\033[0m %s\n" "$1"; }
ok()   { printf "\033[32m✓\033[0m %s\n" "$1"; }
err()  { printf "\033[31m✗ %s\033[0m\n" "$1" >&2; }
bold() { printf "\033[1m%s\033[0m\n" "$1"; }

bold "PrepWell — Prepare smarter. Learn deeper."
echo

# 1) Prerequisites ------------------------------------------------------------
command -v node >/dev/null 2>&1 || { err "Node.js not found — https://nodejs.org"; exit 1; }
command -v ollama >/dev/null 2>&1 || { err "Ollama not found — https://ollama.com/download"; exit 1; }
ok "Node $(node --version)"

# Pick a Python that has prebuilt wheels (3.11–3.13). Avoid 3.14 for now.
PY=""
for c in python3.12 python3.11 python3.13 python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { err "Python 3.11–3.13 not found"; exit 1; }
ok "Python $($PY --version 2>&1 | awk '{print $2}') ($PY)"

# 2) Ollama up + model present ------------------------------------------------
if ! curl -fsS "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1; then
  info "Starting 'ollama serve'…"
  ollama serve >/tmp/prepwell-ollama.log 2>&1 &
  for _ in $(seq 1 30); do
    curl -fsS "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS "${OLLAMA_HOST_URL}/api/tags" >/dev/null 2>&1 || { err "Could not reach Ollama. Run 'ollama serve' manually."; exit 1; }
ok "Ollama is running"
if ! ollama list 2>/dev/null | grep -qiF "${MODEL}"; then
  info "Pulling '${MODEL}' (first run only)…"
  ollama pull "${MODEL}"
fi
ok "Model '${MODEL}' ready"

# 3) Backend venv + deps ------------------------------------------------------
if [ ! -d backend/.venv ]; then
  info "Creating backend virtualenv…"
  "$PY" -m venv backend/.venv
  backend/.venv/bin/pip install -q --upgrade pip
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi
ok "Backend dependencies ready"

# 4) Frontend deps ------------------------------------------------------------
if [ ! -d frontend/node_modules ]; then
  info "Installing frontend dependencies…"
  (cd frontend && npm install --no-audit --no-fund)
fi
ok "Frontend dependencies ready"

# 5) Launch both --------------------------------------------------------------
echo
info "Starting backend on :${BACKEND_PORT} and frontend on :3000"
PREPWELL_PORT="$BACKEND_PORT" backend/.venv/bin/python -m uvicorn app.main:app \
  --app-dir backend --host 0.0.0.0 --port "$BACKEND_PORT" >/tmp/prepwell-backend.log 2>&1 &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null || true' EXIT

# Wait for backend health.
for _ in $(seq 1 30); do
  curl -fsS "http://localhost:${BACKEND_PORT}/api/health" >/dev/null 2>&1 && break
  sleep 1
done
ok "Backend is up (logs: /tmp/prepwell-backend.log)"

echo
bold "PrepWell → http://localhost:3000"
echo "  Student demo: aarav / aarav123     Admin demo: admin / prepwell123"
echo
exec npm --prefix frontend run dev
