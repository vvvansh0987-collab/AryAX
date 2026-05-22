@echo off
REM Setup script for AryaX Platform (Windows)

setlocal enabledelayedexpansion

echo.
echo 🚀 AryaX Platform - Setup Script
echo ==================================
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version
if errorlevel 1 (
    echo ✗ Python not found. Please install Python 3.11+
    exit /b 1
)

REM Create virtual environment (optional)
if not exist "venv" (
    echo ✓ Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo ✓ Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ✗ Failed to install dependencies
    exit /b 1
)

REM Copy environment file
if not exist ".env" (
    echo ✓ Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration
)

REM Create necessary directories
echo ✓ Creating directories...
if not exist "alembic\versions" mkdir alembic\versions
if not exist "k8s" mkdir k8s
if not exist "logs" mkdir logs

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Update .env with your configuration
echo 2. Start services: docker-compose up -d
echo 3. Run development server: python run.py
echo 4. Visit http://localhost:8000/docs for API documentation
echo.

pause
