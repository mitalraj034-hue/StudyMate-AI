@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo         StudyMate AI - Full Development Mode
echo ========================================================
echo.

:: Check Python and Node
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b 1
)

echo [1/3] Ensuring backend directories exist...
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\chroma_db" mkdir "backend\chroma_db"

echo [2/3] Checking database and seeding sample study guide...
python backend/seed_data.py

echo.
echo [3/3] Starting Backend (Port 8000) and Frontend (Port 5173)...
start "StudyMate Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
start "StudyMate Frontend" cmd /k "cd /d "%~dp0frontend" && npm.cmd run dev"

echo.
echo ========================================================
echo Backend API:  http://127.0.0.1:8000
echo Swagger Docs: http://127.0.0.1:8000/docs
echo Frontend Dev: http://localhost:5173
echo ========================================================
echo.
pause
