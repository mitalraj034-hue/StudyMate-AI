@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo         StudyMate AI - Grounded Academic Platform
echo ========================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ and add it to your PATH.
    pause
    exit /b 1
)

echo [1/3] Ensuring uploads and database directories exist...
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\chroma_db" mkdir "backend\chroma_db"

echo [2/3] Verifying database schema and pre-seeded academic study guide...
python backend/seed_data.py

echo.
echo [3/3] Launching StudyMate AI Unified Server on http://127.0.0.1:8000 ...
echo App running at: http://127.0.0.1:8000
echo API Docs at:   http://127.0.0.1:8000/docs
echo.

start http://127.0.0.1:8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

pause
