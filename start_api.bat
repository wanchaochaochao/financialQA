@echo off
REM Financial QA System - API Service Startup Script (Windows)
REM ==========================================================

echo ============================================================
echo 🏦 Financial Asset QA System - API Service
echo ============================================================
echo.

REM Check if FastAPI is installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ❌ FastAPI not installed
    echo    Please run: pip install -r requirements.txt
    exit /b 1
)

echo 📦 Dependencies OK
echo.

echo 📍 Configuration:
echo    Host: 0.0.0.0
echo    Port: 8000
echo    Mode: Development (auto-reload)
echo.

echo 🚀 Starting API server...
echo.
echo 📖 API Documentation: http://localhost:8000/docs
echo 📚 ReDoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

REM Start server
uvicorn ai_agent.api:app --host 0.0.0.0 --port 8000 --reload --log-level info
