@echo off
echo Starting Crop AI Backend Server...
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Flask server...
python app.py
pause
