@echo off
REM ─────────────────────────────────────────────────────────────
REM  PrepWell — one-command launcher (Windows)
REM  Starts the FastAPI backend and the Next.js frontend.
REM  Make sure Ollama is installed and running (ollama serve).
REM ─────────────────────────────────────────────────────────────
setlocal
cd /d "%~dp0"

set "MODEL=%PREPWELL_MODEL%"
if "%MODEL%"=="" set "MODEL=llama3.2:3b"

echo PrepWell - Prepare smarter. Learn deeper.
echo.

where node >nul 2>nul || (echo [X] Node.js not found - https://nodejs.org & exit /b 1)
where ollama >nul 2>nul || (echo [X] Ollama not found - https://ollama.com/download & exit /b 1)
where python >nul 2>nul || (echo [X] Python 3.11-3.13 not found & exit /b 1)

REM Ensure model is present
ollama list | findstr /I "%MODEL%" >nul 2>nul || (echo Pulling %MODEL%... & ollama pull %MODEL%)

REM Backend venv + deps
if not exist backend\.venv (
  echo Creating backend virtualenv...
  python -m venv backend\.venv
  backend\.venv\Scripts\pip install -q --upgrade pip
  backend\.venv\Scripts\pip install -q -r backend\requirements.txt
)

REM Frontend deps
if not exist frontend\node_modules (
  echo Installing frontend dependencies...
  pushd frontend & npm install --no-audit --no-fund & popd
)

echo.
echo Starting backend on :8000 ...
start "PrepWell Backend" backend\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

echo Starting frontend on :3000 ...
echo.
echo PrepWell - http://localhost:3000
echo   Student demo: aarav / aarav123     Admin demo: admin / prepwell123
echo.
npm --prefix frontend run dev

endlocal
