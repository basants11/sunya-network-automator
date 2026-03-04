@echo off
:: SUNYA Unified Autonomous Diagnostic Utility Launcher
:: Version 4.0.0 - Total Autonomous Execution Mode
::
:: This launcher executes the unified autonomous utility with zero user interaction
:: The utility will immediately begin its predetermined workflow upon launch
::
:: NO USER INPUT REQUIRED OR ACCEPTED
:: NO CONFIGURATION OPTIONS
:: NO INTERACTIVE ELEMENTS
:: IMMEDIATE AUTOMATIC EXECUTION

title SUNYA Unified Autonomous Diagnostic Utility v4.0.0
color 0A

echo.
echo ================================================================================
echo  SUNYA UNIFIED AUTONOMOUS NETWORK DIAGNOSTIC UTILITY
echo  Version 4.0.0 - Total Autonomous Execution Mode
echo ================================================================================
echo.
echo  LAUNCHING AUTONOMOUS WORKFLOW...
echo  NO USER INTERACTION REQUIRED OR PERMITTED
echo.
echo  This utility will:
echo   1. Gather system information
echo   2. Enumerate network adapters
echo   3. Test connectivity to multiple targets
echo   4. Perform speed tests
echo   5. Trace network routes
echo   6. Test DNS resolution
echo   7. Calculate health scores
echo   8. Generate ISP complaint summary
echo   9. Create comprehensive reports
echo  10. Export all data to JSON
echo.
echo ================================================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"

:: Check if the unified utility exists
if not exist "%SCRIPT_DIR%..\sunya-unified-autonomous-utility.py" (
    echo ERROR: sunya-unified-autonomous-utility.py not found
    echo Expected location: %SCRIPT_DIR%..\
    pause
    exit /b 1
)

:: Launch the autonomous utility
echo Starting autonomous execution...
echo.

cd /d "%SCRIPT_DIR%.."
python "sunya-unified-autonomous-utility.py"

:: The utility will exit automatically when complete
:: No pause or user interaction follows

exit /b 0
