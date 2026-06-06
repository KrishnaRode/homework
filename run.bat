@echo off
REM ============================================================
REM   File:        run.bat  (repo root)
REM   Description: Convenience wrapper - delegates to the real PrepWell
REM                launcher in prepwell\run.bat so run.bat works from the
REM                repo root too.
REM   Developer:   Krishna Rode
REM   Version:     1
REM ============================================================
cd /d "%~dp0prepwell"
call run.bat %*
