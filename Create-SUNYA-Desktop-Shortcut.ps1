# ==============================================================================
# SUNYA Desktop Master - Shortcut Creator
# ==============================================================================
# Creates a desktop shortcut for the SUNYA Desktop Master tool
# 
# Usage:
#   Right-click this file and select "Run with PowerShell"
#   Or run from command line: powershell -ExecutionPolicy Bypass -File Create-SUNYA-Desktop-Shortcut.ps1
# ==============================================================================

$ErrorActionPreference = "Stop"

# Get paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "SUNYA Desktop Master.lnk"
$TargetPath = Join-Path $ScriptDir "SUNYA-Desktop-Master.bat"

# Colors for output
$Green = "Green"
$Cyan = "Cyan"
$Yellow = "Yellow"
$Red = "Red"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
Write-Host "║                                                                            ║" -ForegroundColor $Cyan
Write-Host "║              🌐 SUNYA DESKTOP MASTER SHORTCUT CREATOR 🌐                   ║" -ForegroundColor $Cyan
Write-Host "║                                                                            ║" -ForegroundColor $Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
Write-Host ""

# Check if target exists
if (-not (Test-Path $TargetPath)) {
    Write-Host "[ERROR] SUNYA-Desktop-Master.bat not found!" -ForegroundColor $Red
    Write-Host "Expected at: $TargetPath" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "Please ensure this script is in the same folder as SUNYA-Desktop-Master.bat"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Target found: $TargetPath" -ForegroundColor $Green
Write-Host "[INFO] Desktop path: $DesktopPath" -ForegroundColor $Green
Write-Host ""

# Check if shortcut already exists
if (Test-Path $ShortcutPath) {
    Write-Host "[!] A shortcut already exists on the Desktop." -ForegroundColor $Yellow
    $replace = Read-Host "Do you want to replace it? (Y/N)"
    if ($replace -ne "Y" -and $replace -ne "y") {
        Write-Host "Operation cancelled."
        exit 0
    }
    Remove-Item $ShortcutPath -Force
}

# Create shortcut
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = $ScriptDir
    $Shortcut.Description = "SUNYA Desktop Master - Launch all network diagnostics and automation tools"
    $Shortcut.IconLocation = "shell32.dll,15"  # Network icon
    $Shortcut.WindowStyle = 1  # Normal window
    
    # Optional: Set hotkey (Ctrl+Alt+S)
    # $Shortcut.HotKey = "CTRL+ALT+S"
    
    $Shortcut.Save()
    
    Write-Host "[SUCCESS] Desktop shortcut created!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "Shortcut details:" -ForegroundColor $Cyan
    Write-Host "  Name: SUNYA Desktop Master.lnk" -ForegroundColor $Green
    Write-Host "  Location: $DesktopPath" -ForegroundColor $Green
    Write-Host "  Target: $TargetPath" -ForegroundColor $Green
    Write-Host ""
    Write-Host "You can now double-click the shortcut on your Desktop to launch SUNYA Desktop Master." -ForegroundColor $Cyan
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to create shortcut: $_" -ForegroundColor $Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Ask if user wants to launch now
$launch = Read-Host "Would you like to launch SUNYA Desktop Master now? (Y/N)"
if ($launch -eq "Y" -or $launch -eq "y") {
    Write-Host ""
    Write-Host "Launching SUNYA Desktop Master..." -ForegroundColor $Cyan
    Start-Process $TargetPath
}

Write-Host ""
Write-Host "Done!" -ForegroundColor $Green
Start-Sleep -Seconds 2
