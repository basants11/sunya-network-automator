@echo off
echo SUNYA Networking - One-Click Automation Tool
echo =============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6+ from https://python.org
    pause
    exit /b 1
)

:: Navigate to script directory
cd /d "%~dp0"

:: Run the one-click automation tool
echo Starting network diagnostic...
python one-click-automation.py

:: Check if script completed successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Diagnostic process failed
    pause
    exit /b 1
)

echo.
echo Diagnostic completed successfully!
pause
