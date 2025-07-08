@echo off
echo 🚀 Starting Mimicking Mindsets Frontend...
echo ================================================

REM Check if we're in the frontend directory
if not exist "package.json" (
    echo ❌ package.json not found. Please run this script from the frontend directory.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo 📋 Frontend Configuration:
echo    • Framework: React + Vite
echo    • Port: 5173 (default)
echo    • Backend API: http://localhost:8000
echo.
echo 🌐 Access URL: http://localhost:5173
echo ================================================
echo.

REM Start the development server
npm run dev

pause 