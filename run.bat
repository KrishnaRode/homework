@echo off
REM ============================================================
REM   Sunday AI Template - one-command launcher (Windows)
REM   Checks Node + Ollama, starts Ollama, pulls the model,
REM   installs deps, then runs the app.
REM   Override the model with:  set MODEL=name && run.bat
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo Free AI. Real Problems. Every Sunday.
echo.

REM 1) Node.js -------------------------------------------------
where node >nul 2>&1
if errorlevel 1 (
  echo [X] Node.js is not installed. Install the LTS version from https://nodejs.org
  exit /b 1
)
for /f "delims=" %%v in ('node --version') do echo [ok] Node.js %%v

REM 2) Ollama --------------------------------------------------
where ollama >nul 2>&1
if errorlevel 1 (
  echo [X] Ollama is not installed. Install it from https://ollama.com/download
  exit /b 1
)
echo [ok] Ollama detected

REM 3) Model ( keep in sync with app.config.ts defaultModel )---
if "%MODEL%"=="" set MODEL=qwen2.5-coder
echo [>] Model: %MODEL%

REM 4) Make sure the Ollama server is up -----------------------
curl -fsS http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
  echo [>] Starting 'ollama serve' in a new window...
  start "ollama" /min ollama serve
  REM wait up to ~30s for it to come online
  for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    curl -fsS http://localhost:11434/api/tags >nul 2>&1
    if not errorlevel 1 goto :serverup
  )
)
:serverup
curl -fsS http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
  echo [X] Could not reach Ollama. Try running 'ollama serve' manually.
  exit /b 1
)
echo [ok] Ollama is running

REM 5) Pull the model if missing -------------------------------
ollama list | findstr /i "%MODEL%" >nul 2>&1
if errorlevel 1 (
  echo [>] Pulling '%MODEL%' (first run only, this can take a few minutes)...
  ollama pull %MODEL%
)
echo [ok] Model '%MODEL%' is ready

REM 6) Install dependencies ------------------------------------
if not exist node_modules (
  echo [>] Installing dependencies...
  call npm install
)
echo [ok] Dependencies installed

REM 7) Launch --------------------------------------------------
echo.
echo Starting the app -^> http://localhost:3000
echo.
call npm run dev
