@echo off
cd /d "%~dp0src"
venv\Scripts\python main.py %*
