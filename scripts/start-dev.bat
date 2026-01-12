@echo off
chcp 65001 >nul
echo ========================================
echo   Kanban System - Dev Environment
echo ========================================
echo.

if not exist "backend" (
    echo Error: Please run this script in project root
    pause
    exit /b 1
)

if not exist "frontend" (
    echo Error: Please run this script in project root
    pause
    exit /b 1
)

echo [1/2] Starting backend service (port 8000)...
start "Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --reload-exclude tests --host 0.0.0.0 --port 8000"

echo [2/2] Starting frontend service (port 5173)...
timeout /t 2 >nul
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Services started!
echo ========================================
echo.
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo.
echo   Press any key to open browser...
pause >nul

start http://localhost:5173
