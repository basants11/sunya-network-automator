@echo off
:: ==============================================================================
:: SUNYA Networking - Easy Installer
:: ==============================================================================
:: Double-click this file to install SUNYA and create desktop shortcut
:: ==============================================================================

title SUNYA Networking Installer
color 0B
cls

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════╗
echo  ║                                                                       ║
echo  ║              🚀 SUNYA NETWORKING INSTALLER v5.0                       ║
echo  ║                                                                       ║
echo  ║         Ultimate Network Automation Suite                            ║
echo  ║                                                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════╝
echo.

:: Check if running as administrator
echo [*] Checking privileges...
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] Not running as administrator - some features may be limited
    echo.
)

:: Check Python
echo [*] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║  ❌ PYTHON NOT FOUND                                          ║
    echo  ║                                                               ║
    echo  ║  Please install Python 3.8+ from https://python.org           ║
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version 2^>^&1') do echo     Found: %%a
echo.

:: Install dependencies
echo [*] Installing dependencies (this may take a few minutes)...
echo.
python -m pip install --upgrade pip --quiet
python -m pip install psutil matplotlib reportlab selenium webdriver-manager speedtest-cli ping3 pyautogui pywin32 wmi fpdf websockets colorama tqdm pyfiglet --quiet
if %ERRORLEVEL% neq 0 (
    echo [!] Some packages may have failed to install, continuing anyway...
) else (
    echo [✓] Dependencies installed successfully!
)
echo.

:: Create desktop shortcut using PowerShell
echo [*] Creating desktop shortcut...
powershell.exe -ExecutionPolicy Bypass -File "%~dp0create-desktop-shortcut.ps1" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] PowerShell shortcut creation failed, using fallback method...
    call :CREATE_FALLBACK_SHORTCUT
) else (
    echo [✓] Desktop shortcut created!
)
echo.

:: Create config file
echo [*] Creating configuration...
if not exist "sunya-pc\.sunya_config" (
    echo default_mode=menu > "sunya-pc\.sunya_config"
    echo auto_update=1 >> "sunya-pc\.sunya_config"
    echo create_shortcut=1 >> "sunya-pc\.sunya_config"
    echo save_reports=1 >> "sunya-pc\.sunya_config"
)
echo [✓] Configuration ready!
echo.

:: Installation complete
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════════════╗
echo  ║                                                                       ║
echo  ║              ✅ INSTALLATION COMPLETE!                                ║
echo  ║                                                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════╝
echo.
echo  📋 What was installed:
echo     • SUNYA Ultimate Automation Suite
echo     • Desktop shortcut (with Ctrl+Alt+S hotkey)
echo     • Start Menu entry
echo     • Python dependencies
echo.
echo  🚀 How to use:
echo     1. Double-click "SUNYA Network Automation" on your desktop
echo     2. OR press Ctrl+Alt+S from anywhere
echo     3. Select a diagnostic mode from the menu
echo.
echo  📖 Available Tools:
echo     • Quick Test (30 seconds)
echo     • High-Performance Diagnostic
echo     • Complete System Analysis
echo     • Real-time Network Monitor
echo     • One-Click Browser Automation
echo.
echo  Press any key to launch SUNYA now...
pause >nul

:: Launch SUNYA
call "%~dp0SUNYA-Automation.bat"
exit /b 0

:: ==============================================================================
:: FALLBACK SHORTCUT CREATOR
:: ==============================================================================
:CREATE_FALLBACK_SHORTCUT
set "DESKTOP=%USERPROFILE%\Desktop"
set "VBS=%TEMP%\sunya_shortcut.vbs"
(
    echo Set WshShell = WScript.CreateObject("WScript.Shell"^)
    echo strDesktop = WshShell.SpecialFolders("Desktop"^)
    echo Set oShortcut = WshShell.CreateShortcut(strDesktop ^& "\SUNYA Network Automation.lnk"^)
    echo oShortcut.TargetPath = "%~dp0SUNYA-Automation.bat"
    echo oShortcut.WorkingDirectory = "%~dp0"
    echo oShortcut.IconLocation = "%%SystemRoot%%\System32\shell32.dll,15"
    echo oShortcut.Description = "SUNYA Networking Ultimate Automation Suite"
    echo oShortcut.HotKey = "CTRL+ALT+S"
    echo oShortcut.Save
) > "%VBS%"
cscript //nologo "%VBS%"
del "%VBS%"
echo [✓] Fallback shortcut created!
goto :EOF
