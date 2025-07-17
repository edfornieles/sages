@echo off
REM Dynamic Character Playground - New Port Launcher
REM This script finds an available port and launches the server

echo 🎭 Dynamic Character Playground - New Port Launcher
echo ==================================================

REM Check if we're in the right directory (from launch folder perspective)
if not exist "..\core\dynamic_character_playground_enhanced.py" (
    echo ❌ Error: Could not find core\dynamic_character_playground_enhanced.py
    echo Please ensure this script is in the launch folder of the project
    pause
    exit /b 1
)

REM Find available port using Python
echo 🔍 Finding available port...
for /f %%i in ('python -c "import socket; s=socket.socket(); s.bind(('localhost', 0)); print(s.getsockname()[1]); s.close()"') do set PORT=%%i

echo ✅ Found available port: %PORT%

REM Change to project root directory
cd ..

REM Launch the server
echo 🚀 Launching Dynamic Character Playground on port %PORT%...
echo 🌐 Server will be available at: http://localhost:%PORT%
echo 🎭 Character Creator: http://localhost:%PORT%/create-character
echo 📊 Health Check: http://localhost:%PORT%/health
echo.
echo ============================================================
echo 🎮 Starting server... (Press Ctrl+C to stop)
echo ============================================================

REM Start the server
python core\dynamic_character_playground_enhanced.py --port=%PORT%

pause 