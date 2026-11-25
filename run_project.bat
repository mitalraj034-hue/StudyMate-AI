@echo off
echo ====================================================
echo Starting StudyMate AI Backend and Frontend...
echo ====================================================

start "StudyMate AI - Backend" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload"

start "StudyMate AI - Frontend" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo Both servers started!
echo Frontend: http://127.0.0.1:5173/
echo Backend:  http://127.0.0.1:8000/
echo Swagger:  http://127.0.0.1:8000/docs
echo ====================================================
