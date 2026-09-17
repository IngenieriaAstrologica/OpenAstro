@echo off
REM OpenAstro.org launcher via WSL (Ubuntu + WSLg)
REM %~dp0 is this file's folder; the trailing "." keeps its final backslash from escaping the quote
wsl -d Ubuntu --cd "%~dp0." bash ./launch.sh
