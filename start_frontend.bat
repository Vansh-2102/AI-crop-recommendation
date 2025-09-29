@echo off
echo Starting Crop AI Frontend Server...
cd /d "%~dp0\frontend"
echo Current directory: %CD%
echo.
echo Starting React development server...
npm start
pause
