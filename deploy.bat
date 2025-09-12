@echo off
REM CloneGallery Deployment Script for Windows
REM This script sets up and deploys the CloneGallery application

echo 🚀 Starting CloneGallery deployment...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service health...

REM Check web service
curl -f http://localhost:3000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web service is running on http://localhost:3000
) else (
    echo ⚠️  Web service may not be ready yet
)

REM Check API service
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API service is running on http://localhost:8000
) else (
    echo ⚠️  API service may not be ready yet
)

REM Initialize database
echo 🗄️  Initializing database...
docker-compose run --rm db-migrate
docker-compose run --rm db-seed

echo.
echo 🎉 Deployment complete!
echo.
echo 📋 Service URLs:
echo    Frontend: http://localhost:3000
echo    API:      http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 🔧 Management Commands:
echo    View logs:    docker-compose logs -f
echo    Stop all:     docker-compose down
echo    Restart:      docker-compose restart
echo    Update:       docker-compose pull ^&^& docker-compose up -d
echo.
echo 📊 Demo Accounts:
echo    Admin:  admin@clonegallery.local
echo    Editor: editor@clonegallery.local
echo    User:   user@clonegallery.local
echo.
echo 🎨 Features Available:
echo    ✅ Image upload with editing (crop, resize, filters)
echo    ✅ AI image generation
echo    ✅ One-like-per-user system
echo    ✅ Database persistence
echo    ✅ Responsive design
echo.
pause
