@echo off
chcp 65001 >nul
title SUNYA Master Diagnostic Tool v5.0.0
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║           SUNYA MASTER DIAGNOSTIC TOOL v5.0.0                    ║
echo ║           Unified Network Diagnostic Platform                    ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Set working directory
cd /d "%~dp0"

:: Check if sunya-master.py exists in root
if exist "sunya-master.py" (
    set "MASTER_SCRIPT=sunya-master.py"
) else if exist "sunya-pc\sunya-master.py" (
    set "MASTER_SCRIPT=sunya-pc\sunya-master.py"
) else (
    echo [ERROR] sunya-master.py not found!
    pause
    exit /b 1
)

echo [INFO] Python detected
echo [INFO] Script: %MASTER_SCRIPT%
echo.

:: Menu
:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    SELECT TEST MODE                              ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo   [1] QUICK Mode      - 30 second network health check
echo   [2] STANDARD Mode   - 2 minute comprehensive diagnostic
echo   [3] FULL Mode       - 5 minute deep diagnostic analysis
echo   [4] Custom Output   - Run with custom output directory
echo   [5] Check Dependencies
echo   [Q] Quit
echo.
set /p choice="Enter choice (1-5, Q): "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto standard
if "%choice%"=="3" goto full
if "%choice%"=="4" goto custom
if "%choice%"=="5" goto deps
if /i "%choice%"=="Q" goto end

goto menu

:quick
echo.
echo [INFO] Starting QUICK mode diagnostic...
python "%MASTER_SCRIPT%" --quick
goto done

:standard
echo.
echo [INFO] Starting STANDARD mode diagnostic...
python "%MASTER_SCRIPT%"
goto done

:full
echo.
echo [INFO] Starting FULL mode diagnostic...
python "%MASTER_SCRIPT%" --full
goto done

:custom
echo.
set /p outdir="Enter output directory path: "
echo [INFO] Starting diagnostic with custom output: %outdir%
python "%MASTER_SCRIPT%" --output "%outdir%"
goto done

:deps
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    CHECKING DEPENDENCIES                         ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo Checking Python packages...
python -c "import psutil; print('  [OK] psutil')" 2>nul || echo   [MISSING] psutil - pip install psutil
echo.

echo Optional packages:
python -c "import speedtest; print('  [OK] speedtest-cli')" 2>nul || echo   [MISSING] speedtest-cli - pip install speedtest-cli
python -c "import selenium; print('  [OK] selenium')" 2>nul || echo   [MISSING] selenium - pip install selenium
python -c "import pyautogui; print('  [OK] pyautogui')" 2>nul || echo   [MISSING] pyautogui - pip install pyautogui
python -c "import wmi; print('  [OK] wmi')" 2>nul || echo   [MISSING] wmi - pip install WMI
python -c "from fpdf import FPDF; print('  [OK] fpdf')" 2>nul || echo   [MISSING] fpdf - pip install fpdf2
echo.

pause
goto menu

:done
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    DIAGNOSTIC COMPLETE                           ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
pause

:end
exit /b 0
