@echo off
REM Docker Quick Start Script for IronOre CRM (Windows)

setlocal enabledelayedexpansion

echo ================================
echo IronOre CRM - Docker Setup
echo ================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop.
    pause
    exit /b 1
)

echo ✓ Docker detected
echo ✓ Docker Compose detected
echo.

REM Check if .env file exists
if not exist .env (
    echo 📋 Creating .env from .env.docker template...
    copy .env.docker .env >nul
    echo ✓ .env file created
    echo.
    echo ⚠️  IMPORTANT: Review and update .env with your configuration:
    echo    - SA_PASSWORD: SQL Server password
    echo    - SECRET_KEY: Generate a secure key
    echo    - SMTP settings: Configure email
    echo.
    echo Edit .env file now and press Enter to continue...
    pause
)

echo.
echo 🏗️  Building Docker images...
call docker-compose build
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo.
echo 🚀 Starting services...
call docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10

echo.
echo 📊 Service Status:
call docker-compose ps

echo.
echo ✓ Services are running!
echo.
echo 🌐 Access points:
echo    • Frontend: http://localhost
echo    • API: http://localhost:8000
echo    • API Docs: http://localhost:8000/docs
echo    • Database: localhost:1433
echo.
echo 📝 Useful commands:
echo    • View logs: docker-compose logs -f
echo    • Stop services: docker-compose down
echo    • View specific service: docker-compose logs -f backend
echo.
pause
