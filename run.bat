@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Python executable not found in .venv. Please make sure the virtual environment is set up at .venv.
    pause
    exit /b 1
)
echo Launching Snake Game in virtual environment...
.venv\Scripts\python main.py
pause
