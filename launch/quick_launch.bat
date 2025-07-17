@echo off
echo 🎭 Enhanced Dynamic Character Playground - Windows Launcher
echo ========================================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run setup first:
    echo python -m venv .venv
    echo .venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate

REM Check if OpenAI API key is set
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  Warning: OPENAI_API_KEY not set
    echo Please set your OpenAI API key:
    echo set OPENAI_API_KEY=your_api_key_here
    echo.
    echo Or set it now (will be temporary):
    set /p OPENAI_API_KEY="Enter your OpenAI API key: "
)

REM Launch the system with auto-port finder
echo 🚀 Launching system with auto-port finder...
python launch\launch_new_port.py

pause 