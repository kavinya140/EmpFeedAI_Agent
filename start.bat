@echo off
echo ========================================
echo  Employee Feedback Agent - Quick Start
echo ========================================
echo.

if not exist .env (
    copy .env.example .env
    echo Created .env file - PLEASE add your GROQ_API_KEY!
    notepad .env
)

echo Starting Docker Desktop required...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Desktop is not running.
    echo Please start Docker Desktop and run this script again.
    pause
    exit /b 1
)

echo Building and starting containers...
docker-compose up --build -d

echo Waiting for services to start...
timeout /t 15 /nobreak >nul

echo Seeding sample data...
docker-compose exec app python scripts/seed_data.py

echo.
echo ========================================
echo  App is running at: http://localhost:8000
echo ========================================
pause
