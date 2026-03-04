@echo off
:: SUNYA ULTRA - One-Click Launcher
:: Version 4.0 - Ultra-Fast Network Automation
::
:: Usage:
::   run-ultra.bat         - Standard diagnostic (2 minutes)
::   run-ultra.bat quick   - Quick diagnostic (30 seconds)
::   run-ultra.bat full    - Full diagnostic (5 minutes)
::   run-ultra.bat open    - Run and open report

title SUNYA ULTRA Network Diagnostic
color 0A
cls

echo ============================================================
echo    SUNYA ULTRA v4.0 - Ultra-Fast Network Automation
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

:: Get mode from argument
set "MODE=%~1"
set "ARGS="

if /I "%MODE%"=="quick" (
    echo Mode: QUICK (30 seconds)
    set "ARGS=--quick"
) else if /I "%MODE%"=="full" (
    echo Mode: FULL (5 minutes)
    set "ARGS=--full"
) else if /I "%MODE%"=="open" (
    echo Mode: STANDARD with auto-open
    set "ARGS=--open"
) else (
    echo Mode: STANDARD (2 minutes)
    echo.
    echo Usage: run-ultra.bat [quick^|full^|open]
)

echo.
echo Starting diagnostic...
echo ============================================================
echo.

:: Run the diagnostic
cd /d "%~dp0"
python sunya-ultra.py %ARGS%

set "EXITCODE=%ERRORLEVEL%"

echo.
echo ============================================================
if %EXITCODE% == 0 (
    echo    Status: HEALTHY - No issues detected
    color 0A
) else if %EXITCODE% == 1 (
    echo    Status: WARNING - Some issues found
    color 0E
) else (
    echo    Status: CRITICAL - Major issues detected
    color 0C
)
echo ============================================================
echo.

:: Auto-pause for user to read results
if /I "%MODE%"=="open" goto :eof

echo Press any key to exit...
pause >nul
