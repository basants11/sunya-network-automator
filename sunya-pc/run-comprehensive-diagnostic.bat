@echo off
echo ================================================
echo  Sunya Networking - Comprehensive Diagnostic Tool
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python first.
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if required dependencies are installed
echo Checking dependencies...
python -c "import psutil, ping3, speedtest, pyautogui, selenium, webdriver_manager, fpdf" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Installing required dependencies...
    pip install -q psutil ping3 speedtest-cli pyautogui selenium webdriver-manager fpdf wmi
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo Dependencies verified successfully!
echo.

echo Starting comprehensive network diagnostics...
echo This will take several minutes to complete.
echo Do NOT close this window until the test is finished.
echo.

REM Run the diagnostic tool
python "%~dp0comprehensive-network-diagnostic.py"

echo.
echo ================================================
echo  Diagnostic process complete!
echo  Check your desktop for the report folder.
echo ================================================
echo.

pause
