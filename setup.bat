@echo off
REM MemoryOS - Windows Setup Script

echo ==================================
echo 🧠 MemoryOS Setup Script (Windows)
echo ==================================
echo.

REM Check Python
echo [1/6] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo   ❌ Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo   ✅ Python detected
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo   ✅ Virtual environment created
) else (
    echo   ⚠️  Virtual environment already exists (skipping)
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo   ✅ Virtual environment activated
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo   ✅ All dependencies installed
echo.

REM Create directories
echo [5/6] Creating directory structure...
if not exist "database" mkdir database
if not exist "database\chroma_db" mkdir database\chroma_db
if not exist "logs" mkdir logs

REM Create initial state file
echo {> database\user_state.json
echo   "user_profile": {},>> database\user_state.json
echo   "entities": {},>> database\user_state.json
echo   "knowledge_base": {},>> database\user_state.json
echo   "events": [],>> database\user_state.json
echo   "system_stats": {"total_turns": 0}>> database\user_state.json
echo }>> database\user_state.json

echo   ✅ Directories and initial files created
echo.

REM Environment setup
echo [6/6] Environment configuration...
if not exist ".env" (
    echo GROQ_API_KEY=your_groq_api_key_here> .env
    echo   ⚠️  Created .env file - PLEASE ADD YOUR GROQ API KEY
) else (
    echo   ✅ .env file already exists
)
echo.

REM Final instructions
echo ==================================
echo ✅ Setup Complete!
echo ==================================
echo.
echo 📋 Next Steps:
echo.
echo 1. Add your Groq API key to .env:
echo    notepad .env
echo.
echo 2. Start the backend (in this terminal):
echo    uvicorn main:app --reload --port 8000
echo.
echo 3. Open a NEW terminal and run:
echo    streamlit run app.py
echo.
echo 4. Open your browser:
echo    http://localhost:8501
echo.
echo ==================================
echo 🎯 Demo Tips:
echo ==================================
echo.
echo • Use the demo buttons for quick scenarios
echo • Check the Analytics tab for visualizations
echo • Run 'python demo_bulk_test.py' for stress testing
echo • Export analytics before presenting
echo.
echo Good luck with the hackathon! 🚀
echo.
pause