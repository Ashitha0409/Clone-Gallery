@echo off
echo Starting CloneGallery locally...

echo Starting Backend API on port 8000...
start "Backend API" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Frontend on port 3000...
start "Frontend" cmd /k "npm run dev"

echo.
echo Services starting...
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul


