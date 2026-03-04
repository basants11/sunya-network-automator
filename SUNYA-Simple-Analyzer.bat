@echo off
:: ==============================================================================
:: SUNYA Simple Desktop Analyzer v1.0
:: ==============================================================================
:: Single-purpose tool: Click button → Analyze → View Report
:: No modes, no options, no menus. Just one button.
:: ==============================================================================

chcp 65001 >nul
title SUNYA Simple Desktop Analyzer
color 0A

setlocal EnableDelayedExpansion

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "ANALYZER_SCRIPT=%SCRIPT_DIR%SUNYA-Simple-Analyzer.py"

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║              🌐 SUNYA SIMPLE DESKTOP ANALYZER v1.0 🌐                      ║
echo ║                                                                            ║
echo ║              Click button → Analyze → View Report                          ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8 or higher.
    echo.
    echo Download Python from: https://www.python.org/downloads/
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
echo [OK] %PYTHON_VERSION% detected
echo.

:: Check if analyzer script exists
if not exist "%ANALYZER_SCRIPT%" (
    echo [ERROR] SUNYA-Simple-Analyzer.py not found!
    echo Expected at: %ANALYZER_SCRIPT%
    pause
    exit /b 1
)

echo [INFO] Starting Simple Desktop Analyzer...
echo.

:: Launch the GUI
cd /d "%SCRIPT_DIR%"
python "%ANALYZER_SCRIPT%"

if errorlevel 1 (
    echo.
    echo [ERROR] Analyzer exited with an error.
    pause
)

endlocal
exit /b 0
