@echo off
chcp 65001 >nul
title SUNYA NET - High-Performance Network Monitor
color 0B

echo ============================================================
echo  SUNYA NET - High-Performance Network Diagnostic System
echo  Version 3.0.0 Ultra
echo ============================================================
echo.
echo  Features:
echo  - Real-time monitoring with 1-2 second updates
echo  - Parallel ping execution (8-10 threads)
echo  - WebSocket dashboard server
echo  - Background PDF generation
echo  - Auto-cleanup and process management
echo  - Adaptive monitoring intervals
echo  - CPU/RAM throttling
echo.
echo ============================================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.7+
    pause
    exit /b 1
)

:: Install required packages if needed
echo [INFO] Checking dependencies...
python -c "import psutil, websockets, chart.js" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    pip install psutil websockets fpdf matplotlib speedtest-cli --quiet
)

echo.
echo [INFO] Starting SUNYA NET Monitor...
echo [INFO] Dashboard will be available at: http://localhost:8765
echo [INFO] Open dashboard.html in your browser
echo.
echo Press Ctrl+C to stop monitoring
echo.

python sunyanet-high-performance.py

if errorlevel 1 (
    echo.
    echo [ERROR] Monitor encountered an error.
    echo [INFO] Check the error message above.
    pause
)

echo.
echo [INFO] Monitor stopped.
pause
