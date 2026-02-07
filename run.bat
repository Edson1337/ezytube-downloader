@echo off
cd /d "%~dp0"
set "PATH=%~dp0bin;%PATH%"
uv run python src/main.py
