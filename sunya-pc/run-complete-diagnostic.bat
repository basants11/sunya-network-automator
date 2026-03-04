@echo off
chcp 65001 >nul
title SUNYA Complete Network Diagnostic System
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║        SUNYA COMPLETE NETWORK DIAGNOSTIC SYSTEM               ║
echo  ║                                                               ║
echo  ║     Professional Windows Network Diagnostic Tool v2.0         ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  This tool will perform comprehensive network diagnostics:
echo    • Network adapter analysis with driver inspection
echo    • Internet speed tests (fast.com, speedtest.net)
echo    • Multi-target ping tests (60 seconds each)
echo    • Load/stress testing with 1000 packets
echo    • WinMTR route tracing
echo    • Intelligent health scoring (0-100)
echo    • Visual charts generation
echo    • Professional PDF report
echo.
echo  Press any key to start or Ctrl+C to cancel...
pause >nul

echo.
echo  [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
echo  [OK] Python found

echo.
echo  [*] Installing required dependencies...
python -m pip install --quiet wmi psutil matplotlib reportlab selenium webdriver-manager speedtest-cli ping3 pyautogui pywin32 2>nul
echo  [OK] Dependencies ready

echo.
echo  [*] Starting diagnostic process...
echo  [*] This may take 5-10 minutes depending on your connection
echo.

cd /d "%~dp0"
python "sunya-complete-diagnostic.py"

echo.
if errorlevel 1 (
    echo  [ERROR] Diagnostic failed
    pause
    exit /b 1
) else (
    echo  [SUCCESS] Diagnostic completed successfully!
    echo  [*] Check your Desktop for the report folder
    pause
)
