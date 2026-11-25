Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Starting StudyMate AI Backend & Frontend..." -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
if (-not $root) { $root = Get-Location }

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; Write-Host 'Starting Backend (FastAPI)...' -ForegroundColor Green; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; Write-Host 'Starting Frontend (Vite)...' -ForegroundColor Green; npm.cmd run dev"

Write-Host "`nBoth servers launched in separate windows!" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:5173/" -ForegroundColor Yellow
Write-Host "Backend:  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
