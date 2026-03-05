@echo off
cd /d "%~dp0"
call venv\Scripts\activate >nul 2>&1
cd src
python main.py %*