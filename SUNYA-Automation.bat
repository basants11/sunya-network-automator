@echo off
:: ==============================================================================
:: SUNYA NETWORKING - ULTIMATE AUTOMATION SUITE v5.0
:: ==============================================================================
:: A powerful unified automation tool that combines all SUNYA diagnostic tools
:: into one easy-to-use interface with desktop shortcut support.
::
:: Features:
::   ✓ 8 Different diagnostic modes
::   ✓ Automatic dependency management
::   ✓ Desktop shortcut creation
::   ✓ System health monitoring
::   ✓ Report management
::   ✓ Auto-update capability
::   ✓ Configuration profiles
:: ==============================================================================

setlocal EnableDelayedExpansion
chcp 65001 >nul

:: ==============================================================================
:: CONFIGURATION
:: ==============================================================================
set "VERSION=5.0.0"
set "TOOL_NAME=SUNYA Ultimate Automation"
set "SCRIPT_DIR=%~dp0sunya-pc"
set "DESKTOP_PATH=%USERPROFILE%\Desktop"
set "CONFIG_FILE=%SCRIPT_DIR%\.sunya_config"
set "LOG_FILE=%SCRIPT_DIR%\automation.log"

:: Colors
set "COLOR_HEADER=0B"
set "COLOR_MENU=0E"
set "COLOR_SUCCESS=0A"
set "COLOR_ERROR=0C"
set "COLOR_INFO=0F"

:: ==============================================================================
:: INITIALIZATION
:: ==============================================================================
:INIT
call :CHECK_ADMIN
call :CHECK_PYTHON
call :LOAD_CONFIG
call :MAIN_MENU

:: ==============================================================================
:: CHECK ADMIN PRIVILEGES
:: ==============================================================================
:CHECK_ADMIN
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo  ⚠ WARNING: Not running as Administrator
    echo  Some features may be limited.
    echo  Right-click and "Run as administrator" for full functionality.
    echo.
    timeout /t 3 >nul
)
goto :EOF

:: ==============================================================================
:: CHECK PYTHON INSTALLATION
:: ==============================================================================
:CHECK_PYTHON
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color %COLOR_ERROR%
    cls
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║                                                               ║
    echo  ║  ❌ PYTHON NOT FOUND                                          ║
    echo  ║                                                               ║
    echo  ║  Python 3.8 or higher is required to run this tool.          ║
    echo  ║                                                               ║
    echo  ║  Please install Python from:                                  ║
    echo  ║  https://www.python.org/downloads/                           ║
    echo  ║                                                               ║
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
goto :EOF

:: ==============================================================================
:: LOAD CONFIGURATION
:: ==============================================================================
:LOAD_CONFIG
if not exist "%CONFIG_FILE%" (
    echo default_mode=menu > "%CONFIG_FILE%"
    echo auto_update=1 >> "%CONFIG_FILE%"
    echo create_shortcut=1 >> "%CONFIG_FILE%"
    echo save_reports=1 >> "%CONFIG_FILE%"
)
for /f "tokens=1,2 delims==" %%a in ('type "%CONFIG_FILE%"') do set "CONFIG_%%a=%%b"
goto :EOF

:: ==============================================================================
:: SAVE CONFIGURATION
:: ==============================================================================
:SAVE_CONFIG
(
    echo default_mode=%CONFIG_default_mode%
    echo auto_update=%CONFIG_auto_update%
    echo create_shortcut=%CONFIG_create_shortcut%
    echo save_reports=%CONFIG_save_reports%
) > "%CONFIG_FILE%"
goto :EOF

:: ==============================================================================
:: MAIN MENU
:: ==============================================================================
:MAIN_MENU
:MENU_START
cls
color %COLOR_HEADER%
echo.
echo  ╔═══════════════════════════════════════════════════════════════════════╗
echo  ║                                                                       ║
echo  ║     🚀 SUNYA NETWORKING - ULTIMATE AUTOMATION SUITE v%VERSION%          ║
echo  ║                                                                       ║
echo  ║     %PYTHON_VERSION%                                            ║
echo  ║                                                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════╝
echo.
color %COLOR_MENU%
echo  ╔═══════════════════════════════════════════════════════════════════════╗
echo  ║  📊 QUICK DIAGNOSTICS                                                 ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║                                                                       ║
echo  ║   [1] ⚡ Ultra-Fast Quick Test     - 30 seconds, essential checks    ║
echo  ║   [2] 🔥 High-Performance Test     - 5 minutes, optimized speed      ║
echo  ║   [3] 🎯 One-Click Automation      - Browser-based full diagnostic   ║
echo  ║                                                                       ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║  🔍 COMPREHENSIVE DIAGNOSTICS                                         ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║                                                                       ║
echo  ║   [4] 📋 Complete Diagnostic       - Full system analysis            ║
echo  ║   [5] 🌐 Comprehensive Network     - Deep network inspection         ║
echo  ║   [6] 🖥️  SunyaNet Monitor         - Real-time monitoring            ║
echo  ║                                                                       ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║  🛠️  TOOLS ^& UTILITIES                                                 ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║                                                                       ║
echo  ║   [7] 🔧 SunyaTroubleshoot         - Automatic troubleshooting       ║
echo  ║   [8] 📈 Dashboard Viewer          - Open HTML dashboard             ║
echo  ║   [9] 🔄 Install Dependencies      - Install/update all packages     ║
echo  ║                                                                       ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║  ⚙️  SYSTEM OPTIONS                                                     ║
echo  ╠═══════════════════════════════════════════════════════════════════════╣
echo  ║                                                                       ║
echo  ║   [C] 🖥️  Create Desktop Shortcut   - Add shortcut to desktop         ║
echo  ║   [S] 📂 Open Reports Folder       - View all saved reports          ║
echo  ║   [U] ⬆️  Check for Updates        - Update SUNYA tools              ║
echo  ║   [A] ⚙️  Advanced Settings         - Configure automation            ║
echo  ║   [H] ❓ Help ^& Documentation      - View usage guide                ║
echo  ║                                                                       ║
echo  ║   [Q] 🚪 Quit                      - Exit application                ║
echo  ║                                                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════╝
echo.
color %COLOR_INFO%
set /p choice="  Enter your choice [1-9,C,S,U,A,H,Q]: "

echo.

if /I "%choice%"=="1" goto :RUN_ULTRA_QUICK
if /I "%choice%"=="2" goto :RUN_HIGH_PERF
if /I "%choice%"=="3" goto :RUN_ONECLICK
if /I "%choice%"=="4" goto :RUN_COMPLETE
if /I "%choice%"=="5" goto :RUN_COMPREHENSIVE
if /I "%choice%"=="6" goto :RUN_SUNYANET
if /I "%choice%"=="7" goto :RUN_SUNYATSHOOT
if /I "%choice%"=="8" goto :OPEN_DASHBOARD
if /I "%choice%"=="9" goto :INSTALL_DEPS
if /I "%choice%"=="C" goto :CREATE_SHORTCUT
if /I "%choice%"=="S" goto :OPEN_REPORTS
if /I "%choice%"=="U" goto :CHECK_UPDATES
if /I "%choice%"=="A" goto :ADVANCED_SETTINGS
if /I "%choice%"=="H" goto :SHOW_HELP
if /I "%choice%"=="Q" goto :QUIT
goto :INVALID_CHOICE

:: ==============================================================================
:: RUN ULTRA QUICK TEST
:: ==============================================================================
:RUN_ULTRA_QUICK
call :HEADER "⚡ ULTRA-FAST QUICK TEST"
echo  Starting 30-second quick diagnostic...
echo.
cd /d "%SCRIPT_DIR%"
python sunya-ultra.py --quick
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: RUN HIGH PERFORMANCE TEST
:: ==============================================================================
:RUN_HIGH_PERF
call :HEADER "🔥 HIGH-PERFORMANCE DIAGNOSTIC"
echo.
echo  Select test mode:
echo    [1] Quick Test     - 10 cycles (~5 minutes)
echo    [2] Standard Test  - 30 cycles (~15 minutes)
echo    [3] Extended Test  - 100 cycles (~1 hour)
echo    [4] Continuous     - Until stopped
echo.
set /p hp_choice="  Select mode [1-4]: "

cd /d "%SCRIPT_DIR%"
if "%hp_choice%"=="1" python sunya-high-performance-diagnostic.py --quick
if "%hp_choice%"=="2" python sunya-high-performance-diagnostic.py --standard
if "%hp_choice%"=="3" python sunya-high-performance-diagnostic.py --extended
if "%hp_choice%"=="4" python sunya-high-performance-diagnostic.py --continuous
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: RUN ONE-CLICK AUTOMATION
:: ==============================================================================
:RUN_ONECLICK
call :HEADER "🎯 ONE-CLICK AUTOMATION"
echo  This will run browser-based diagnostics using Chrome.
echo  Make sure Chrome is installed.
echo.
cd /d "%SCRIPT_DIR%"
python one-click-automation.py
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: RUN COMPLETE DIAGNOSTIC
:: ==============================================================================
:RUN_COMPLETE
call :HEADER "📋 COMPLETE NETWORK DIAGNOSTIC"
echo  This will perform a comprehensive system analysis.
echo  Estimated time: 5-10 minutes
echo.
cd /d "%SCRIPT_DIR%"
python sunya-complete-diagnostic.py
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: RUN COMPREHENSIVE DIAGNOSTIC
:: ==============================================================================
:RUN_COMPREHENSIVE
call :HEADER "🌐 COMPREHENSIVE NETWORK DIAGNOSTIC"
echo  This will perform deep network inspection.
echo  Estimated time: 10-15 minutes
echo.
cd /d "%SCRIPT_DIR%"
python comprehensive-network-diagnostic.py
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: RUN SUNYANET MONITOR
:: ==============================================================================
:RUN_SUNYANET
call :HEADER "🖥️  SUNYANET REAL-TIME MONITOR"
echo  Starting real-time network monitoring...
echo  Dashboard: http://localhost:8765
echo  Press Ctrl+C to stop
echo.
cd /d "%SCRIPT_DIR%"
python sunyanet-high-performance.py
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: RUN SUNYATSHOOT
:: ==============================================================================
:RUN_SUNYATSHOOT
call :HEADER "🔧 SUNYATSHOOT TROUBLESHOOTING"
echo  Running automatic network troubleshooting...
echo.
cd /d "%SCRIPT_DIR%"
python sunyatshoot.py
call :COMPLETION_STATUS %ERRORLEVEL%
pause
goto :MENU_START

:: ==============================================================================
:: OPEN DASHBOARD
:: ==============================================================================
:OPEN_DASHBOARD
call :HEADER "📈 OPENING DASHBOARD"
if exist "%SCRIPT_DIR%\dashboard.html" (
    start "" "%SCRIPT_DIR%\dashboard.html"
    echo  Dashboard opened in browser.
) else (
    echo  ❌ Dashboard file not found.
    echo  Run a diagnostic first to generate the dashboard.
)
timeout /t 2 >nul
goto :MENU_START

:: ==============================================================================
:: INSTALL DEPENDENCIES
:: ==============================================================================
:INSTALL_DEPS
call :HEADER "🔄 INSTALLING DEPENDENCIES"
echo  This will install/update all required Python packages.
echo.
echo  [*] Installing core dependencies...
python -m pip install --upgrade pip
python -m pip install psutil matplotlib reportlab selenium webdriver-manager speedtest-cli ping3 pyautogui pywin32 wmi fpdf websockets colorama tqdm pyfiglet
echo.
echo  ✅ Dependencies installed successfully!
pause
goto :MENU_START

:: ==============================================================================
:: CREATE DESKTOP SHORTCUT
:: ==============================================================================
:CREATE_SHORTCUT
call :HEADER "🖥️  CREATING DESKTOP SHORTCUT"
echo  Creating shortcut on Desktop...
echo.

:: Create VBScript to make shortcut
set "VBS_FILE=%TEMP%\CreateShortcut.vbs"
(
    echo Set WshShell = WScript.CreateObject("WScript.Shell"^)
    echo strDesktop = WshShell.SpecialFolders("Desktop"^)
    echo Set oShortcut = WshShell.CreateShortcut(strDesktop ^& "\SUNYA Network Automation.lnk"^)
    echo oShortcut.TargetPath = "%~f0"
    echo oShortcut.WorkingDirectory = "%~dp0"
    echo oShortcut.IconLocation = "%%SystemRoot%%\System32\shell32.dll,15"
    echo oShortcut.Description = "SUNYA Networking Ultimate Automation Suite"
    echo oShortcut.HotKey = "CTRL+ALT+S"
    echo oShortcut.Save
) > "%VBS_FILE%"

cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%"

if exist "%DESKTOP_PATH%\SUNYA Network Automation.lnk" (
    echo  ✅ Shortcut created successfully!
    echo  Location: %DESKTOP_PATH%\SUNYA Network Automation.lnk
    echo  Hotkey: Ctrl+Alt+S
) else (
    echo  ❌ Failed to create shortcut.
)
pause
goto :MENU_START

:: ==============================================================================
:: OPEN REPORTS FOLDER
:: ==============================================================================
:OPEN_REPORTS
call :HEADER "📂 OPENING REPORTS FOLDER"
if exist "%DESKTOP_PATH%\SUNYA_Networking" (
    start explorer "%DESKTOP_PATH%\SUNYA_Networking"
    echo  Reports folder opened.
) else (
    echo  No reports folder found yet.
    echo  Run a diagnostic first to generate reports.
)
pause
goto :MENU_START

:: ==============================================================================
:: CHECK FOR UPDATES
:: ==============================================================================
:CHECK_UPDATES
call :HEADER "⬆️  CHECKING FOR UPDATES"
echo  Checking for SUNYA tool updates...
echo  Current version: %VERSION%
echo.
echo  [*] Checking Python packages...
python -m pip list --outdated | findstr /I "psutil matplotlib selenium reportlab"
echo.
echo  To update all packages, use option [9] Install Dependencies.
pause
goto :MENU_START

:: ==============================================================================
:: ADVANCED SETTINGS
:: ==============================================================================
:ADVANCED_SETTINGS
call :HEADER "⚙️  ADVANCED SETTINGS"
echo.
echo  Current Configuration:
echo    Default Mode: %CONFIG_default_mode%
echo    Auto Update:  %CONFIG_auto_update%
echo    Shortcut:     %CONFIG_create_shortcut%
echo    Save Reports: %CONFIG_save_reports%
echo.
echo  Options:
echo   [1] Toggle Auto-Update (currently: %CONFIG_auto_update%)
echo   [2] Toggle Auto-Shortcut (currently: %CONFIG_create_shortcut%)
echo   [3] Toggle Save Reports (currently: %CONFIG_save_reports%)
echo   [4] Reset to Defaults
echo   [5] Back to Main Menu
echo.
set /p settings_choice="  Select option [1-5]: "

if "%settings_choice%"=="1" (
    if "%CONFIG_auto_update%"=="1" (set "CONFIG_auto_update=0") else (set "CONFIG_auto_update=1")
    call :SAVE_CONFIG
)
if "%settings_choice%"=="2" (
    if "%CONFIG_create_shortcut%"=="1" (set "CONFIG_create_shortcut=0") else (set "CONFIG_create_shortcut=1")
    call :SAVE_CONFIG
)
if "%settings_choice%"=="3" (
    if "%CONFIG_save_reports%"=="1" (set "CONFIG_save_reports=0") else (set "CONFIG_save_reports=1")
    call :SAVE_CONFIG
)
if "%settings_choice%"=="4" (
    set "CONFIG_default_mode=menu"
    set "CONFIG_auto_update=1"
    set "CONFIG_create_shortcut=1"
    set "CONFIG_save_reports=1"
    call :SAVE_CONFIG
)
goto :MENU_START

:: ==============================================================================
:: SHOW HELP
:: ==============================================================================
:SHOW_HELP
call :HEADER "❓ HELP ^& DOCUMENTATION"
echo.
echo  SUNYA Networking Ultimate Automation Suite
echo  ===========================================
echo.
echo  This tool provides comprehensive network diagnostics:
echo.
echo  QUICK TESTS:
echo    • Ultra Quick Test: Fast 30-second diagnostic
echo    • High-Performance: Optimized for speed with parallel execution
echo    • One-Click: Automated browser-based testing
echo.
echo  COMPREHENSIVE TESTS:
echo    • Complete Diagnostic: Full system analysis with PDF reports
echo    • Comprehensive: Deep network inspection and route tracing
echo    • SunyaNet Monitor: Real-time continuous monitoring
echo.
echo  KEYBOARD SHORTCUTS:
echo    • Ctrl+Alt+S: Launch SUNYA (after creating shortcut)
echo.
echo  SUPPORT:
echo    For issues, check the log file: %LOG_FILE%
echo.
pause
goto :MENU_START

:: ==============================================================================
:: INVALID CHOICE
:: ==============================================================================
:INVALID_CHOICE
call :HEADER "❌ INVALID CHOICE"
echo  Please select a valid option from the menu.
timeout /t 2 >nul
goto :MENU_START

:: ==============================================================================
:: QUIT
:: ==============================================================================
:QUIT
call :HEADER "👋 THANK YOU FOR USING SUNYA"
echo  Exiting SUNYA Ultimate Automation Suite...
echo  Have a great day!
timeout /t 2 >nul
exit /b 0

:: ==============================================================================
:: HELPER FUNCTIONS
:: ==============================================================================
:HEADER
color %COLOR_HEADER%
cls
echo.
echo  ╔═══════════════════════════════════════════════════════════════════════╗
echo  ║   %~1
  ║
echo  ╚═══════════════════════════════════════════════════════════════════════╝
echo.
color %COLOR_INFO%
goto :EOF

:COMPLETION_STATUS
if %1 equ 0 (
    color %COLOR_SUCCESS%
    echo.
    echo  ✅ Operation completed successfully!
) else (
    color %COLOR_ERROR%
    echo.
    echo  ❌ Operation completed with errors (Code: %1)
)
color %COLOR_INFO%
goto :EOF
