@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" start_server.py > server_out.log 2>&1
