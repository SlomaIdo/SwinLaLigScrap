@echo off
REM Quick launcher for Swimming Dashboard on Windows

echo ========================================================
echo Swimming Performance Analysis Dashboard
echo ========================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the dashboard
python run_dashboard.py

pause
