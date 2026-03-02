@echo off
echo ==============================================
echo   SUNYATSHOOT - Automatic Network Diagnostic
echo ==============================================
echo.
echo This tool will automatically start running when launched.
echo Do not close this window while the diagnostic is running.
echo.
echo Starting Sunyatshoot...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the Python script
python sunyatshoot.py

echo.
echo Diagnostic completed. Press any key to exit...
pause >nul
