@echo off
:: ==============================================================================
:: SUNYA DESKTOP MASTER LAUNCHER v6.0.0
:: ==============================================================================
:: One tool to rule them all - Launch all SUNYA operations from Desktop
::
:: Features:
::   ✓ Launch any diagnostic tool with one click
::   ✓ System tray integration
::   ✓ Desktop shortcut management
::   ✓ Unified dashboard
::   ✓ Quick access to all tools
::
:: Usage:
::   Double-click this file to open the Desktop Master
::   Run with --create-shortcut to add to desktop
:: ==============================================================================

chcp 65001 >nul
title SUNYA Desktop Master v6.0.0
color 0A

setlocal EnableDelayedExpansion

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "MASTER_SCRIPT=%SCRIPT_DIR%SUNYA-Desktop-Master.py"
set "DESKTOP_PATH=%USERPROFILE%\Desktop"

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║              🌐 SUNYA DESKTOP MASTER v6.0.0 🌐                             ║
echo ║                                                                            ║
echo ║              One Tool to Rule Them All                                     ║
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

:: Handle command line arguments
if "%~1"=="--create-shortcut" goto CREATE_SHORTCUT
if "%~1"=="--help" goto SHOW_HELP
if "%~1"=="-h" goto SHOW_HELP

:: Check if master script exists
if not exist "%MASTER_SCRIPT%" (
    echo [ERROR] SUNYA-Desktop-Master.py not found!
    echo Expected at: %MASTER_SCRIPT%
    pause
    exit /b 1
)

echo [INFO] Starting Desktop Master...
echo [INFO] Script: %MASTER_SCRIPT%
echo.

:: Launch the GUI
cd /d "%SCRIPT_DIR%"
python "%MASTER_SCRIPT%"

if errorlevel 1 (
    echo.
    echo [ERROR] Desktop Master exited with an error.
    pause
)

goto END

:: ==============================================================================
:: CREATE DESKTOP SHORTCUT
:: ==============================================================================
:CREATE_SHORTCUT
echo.
echo Creating desktop shortcut...
echo.

:: Create PowerShell script for shortcut creation
set "PS_SCRIPT=%TEMP%\create_sunya_shortcut.ps1"
(
echo # Create SUNYA Desktop Master shortcut
echo $WshShell = New-Object -comObject WScript.Shell
echo $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\SUNYA Desktop Master.lnk")
echo $Shortcut.TargetPath = "%~f0"
echo $Shortcut.WorkingDirectory = "%SCRIPT_DIR%"
echo $Shortcut.Description = "SUNYA Desktop Master - Launch all network diagnostics"
echo $Shortcut.IconLocation = "shell32.dll,15"
echo $Shortcut.Save()
echo Write-Host "Shortcut created successfully!" -ForegroundColor Green
) > "%PS_SCRIPT%"

:: Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

if exist "%PS_SCRIPT%" del "%PS_SCRIPT%"

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║  ✓ Desktop shortcut created successfully!                                  ║
echo ║                                                                            ║
echo ║  You can now find "SUNYA Desktop Master" on your Desktop.                  ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
pause
goto END

:: ==============================================================================
:: SHOW HELP
:: ==============================================================================
:SHOW_HELP
echo.
echo SUNYA Desktop Master - Command Line Options
echo ============================================
echo.
echo Usage: SUNYA-Desktop-Master.bat [options]
echo.
echo Options:
echo   --create-shortcut    Create a shortcut on the Desktop
echo   --help, -h           Show this help message
echo.
echo Examples:
echo   SUNYA-Desktop-Master.bat                    Start the Desktop Master
echo   SUNYA-Desktop-Master.bat --create-shortcut  Create desktop shortcut
echo.
echo Features:
echo   • Launch any diagnostic tool with one click
echo   • Quick access to all SUNYA operations
echo   • Real-time system status monitoring
echo   • Activity logging
echo   • Dashboard integration
echo.
echo Tools Available:
echo   • Master Diagnostic (Quick/Standard/Full modes)
echo   • Comprehensive Diagnostic
echo   • High Performance Diagnostic
echo   • Unified Autonomous Utility
echo   • Ultra Diagnostic
echo   • Complete Diagnostic
echo   • One-Click Automation
echo   • SunyaNet High Performance
echo   • SunyaTroubleshoot
echo   • Web Dashboard
echo.
pause
goto END

:END
endlocal
exit /b 0
