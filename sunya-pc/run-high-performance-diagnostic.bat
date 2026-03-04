@echo off
chcp 65001 >nul
cls

:: SUNYA High-Performance Network Diagnostic Launcher
:: Maximum Speed & Efficiency Version 3.0

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║       SUNYA HIGH-PERFORMANCE NETWORK DIAGNOSTIC v3.0          ║
echo ║                                                               ║
echo ║              Maximum Speed ^& Efficiency Edition              ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

:: Display Python version
for /f "tokens=*" %%a in ('python --version 2^>^&1') do echo [OK] Found: %%a
echo.

:: Install required packages if needed
echo Checking dependencies...
python -c "import selenium" 2>nul || (
    echo [INFO] Installing selenium...
    pip install selenium webdriver-manager -q
)
python -c "import psutil" 2>nul || (
    echo [INFO] Installing psutil...
    pip install psutil -q
)
python -c "import reportlab" 2>nul || (
    echo [INFO] Installing reportlab...
    pip install reportlab -q
)
python -c "import matplotlib" 2>nul || (
    echo [INFO] Installing matplotlib...
    pip install matplotlib -q
)

echo [OK] Dependencies ready
echo.

:: Menu
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║  SELECT DIAGNOSTIC MODE:                                      ║
echo ║                                                               ║
echo ║  [1] Quick Test (10 cycles, ~5 minutes)                      ║
echo ║      └─ Fast diagnostic with all optimizations               ║
echo ║                                                               ║
echo ║  [2] Standard Test (30 cycles, ~15 minutes)                  ║
echo ║      └─ Comprehensive monitoring with parallel execution     ║
echo ║                                                               ║
echo ║  [3] Extended Test (100 cycles, ~1 hour)                     ║
echo ║      └─ Long-term stability analysis                         ║
echo ║                                                               ║
echo ║  [4] Custom Test (configure your own)                        ║
echo ║      └─ Advanced options for power users                     ║
echo ║                                                               ║
echo ║  [5] Continuous Monitoring (until stopped)                   ║
echo ║      └─ Run indefinitely with adaptive intervals             ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto standard
if "%choice%"=="3" goto extended
if "%choice%"=="4" goto custom
if "%choice%"=="5" goto continuous
echo Invalid choice, defaulting to standard test...
goto standard

:quick
echo.
echo [MODE] Quick Test - 10 Cycles
echo Starting high-performance diagnostic...
python sunya-high-performance-diagnostic.py --cycles 10 --workers 8 --stable-interval 10 --unstable-interval 2 --skip-speed-stable
goto end

:standard
echo.
echo [MODE] Standard Test - 30 Cycles
echo Starting high-performance diagnostic...
python sunya-high-performance-diagnostic.py --cycles 30 --workers 8 --stable-interval 10 --unstable-interval 2 --skip-speed-stable
goto end

:extended
echo.
echo [MODE] Extended Test - 100 Cycles
echo Starting high-performance diagnostic...
python sunya-high-performance-diagnostic.py --cycles 100 --workers 8 --stable-interval 15 --unstable-interval 2 --skip-speed-stable
goto end

:continuous
echo.
echo [MODE] Continuous Monitoring
echo Press Ctrl+C to stop at any time...
python sunya-high-performance-diagnostic.py --workers 8 --stable-interval 10 --unstable-interval 2 --skip-speed-stable
goto end

:custom
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║  CUSTOM TEST CONFIGURATION                                    ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

set /p cycles="Number of cycles (leave blank for continuous): "
set /p duration="Duration in minutes (leave blank for cycle-based): "
set /p workers="Number of parallel workers [8]: "
if "!workers!"=="" set workers=8

set /p stable_int="Stable network interval seconds [10]: "
if "!stable_int!"=="" set stable_int=10

set /p unstable_int="Unstable network interval seconds [2]: "
if "!unstable_int!"=="" set unstable_int=2

set /p max_hops="Max PathPing hops [20]: "
if "!max_hops!"=="" set max_hops=20

echo.
echo Select additional options:
echo [1] Skip speed test when stable (faster)
echo [2] Always run speed tests
set /p speed_opt="Choice [1]: "
if "!speed_opt!"=="2" (
    set skip_speed=
) else (
    set skip_speed=--skip-speed-stable
)

echo.
echo Starting custom diagnostic...
echo.

if "!cycles!"=="" (
    if "!duration!"=="" (
        python sunya-high-performance-diagnostic.py --workers !workers! --stable-interval !stable_int! --unstable-interval !unstable_int! --max-hops !max_hops! !skip_speed!
    ) else (
        python sunya-high-performance-diagnostic.py --duration !duration! --workers !workers! --stable-interval !stable_int! --unstable-interval !unstable_int! --max-hops !max_hops! !skip_speed!
    )
) else (
    if "!duration!"=="" (
        python sunya-high-performance-diagnostic.py --cycles !cycles! --workers !workers! --stable-interval !stable_int! --unstable-interval !unstable_int! --max-hops !max_hops! !skip_speed!
    ) else (
        python sunya-high-performance-diagnostic.py --cycles !cycles! --duration !duration! --workers !workers! --stable-interval !stable_int! --unstable-interval !unstable_int! --max-hops !max_hops! !skip_speed!
    )
)
goto end

:end
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║              DIAGNOSTIC COMPLETED                             ║
echo ║                                                               ║
echo ║  Check your Desktop for the SUNYA_HP_Diagnostic_ folder      ║
echo ║  containing reports, logs, and data.                          ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Auto-open the report folder
for /d %%D in ("%USERPROFILE%\Desktop\SUNYA_HP_Diagnostic_*") do (
    echo Opening report folder: %%D
    start "" "%%D"
    goto folder_opened
)
:folder_opened

echo.
pause
