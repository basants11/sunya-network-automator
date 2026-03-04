# ==============================================================================
# SUNYA Networking - Desktop Shortcut Creator
# ==============================================================================
# This PowerShell script creates a professional desktop shortcut with:
# - Custom icon from system icons
# - Keyboard shortcut (Ctrl+Alt+S)
# - Proper working directory
# - Administrative privileges option
# ==============================================================================

param(
    [string]$ShortcutName = "SUNYA Network Automation",
    [string]$HotKey = "CTRL+ALT+S"
)

# Get paths
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ScriptPath = Join-Path $PSScriptRoot "SUNYA-Automation.bat"
$WorkingDirectory = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SUNYA Desktop Shortcut Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if main script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: SUNYA-Automation.bat not found!" -ForegroundColor Red
    Write-Host "Expected at: $ScriptPath" -ForegroundColor Yellow
    exit 1
}

# Create WScript.Shell COM object
$WshShell = New-Object -ComObject WScript.Shell

# Define shortcut path
$ShortcutPath = Join-Path $DesktopPath "$ShortcutName.lnk"

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ScriptPath
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.Description = "SUNYA Networking Ultimate Automation Suite v5.0"

# Set icon - use network-related icon from shell32.dll
$Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,15"

# Set hotkey
$Shortcut.HotKey = $HotKey

# Window style: 1 = Normal
$Shortcut.WindowStyle = 1

# Save shortcut
$Shortcut.Save()

# Verify creation
if (Test-Path $ShortcutPath) {
    Write-Host "SUCCESS! Desktop shortcut created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Shortcut Details:" -ForegroundColor Cyan
    Write-Host "   Name: $ShortcutName"
    Write-Host "   Location: $ShortcutPath"
    Write-Host "   Hotkey: $HotKey"
    Write-Host "   Target: $ScriptPath"
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "   Double-click the shortcut to open SUNYA"
    Write-Host "   Press $HotKey to launch instantly"
    Write-Host ""
    Write-Host "Tip: Right-click the shortcut and select Run as administrator" -ForegroundColor Magenta
    Write-Host "for full functionality including advanced network diagnostics."
} else {
    Write-Host "Failed to create shortcut!" -ForegroundColor Red
    exit 1
}

# Create additional Start Menu shortcut
$StartMenuPath = [Environment]::GetFolderPath("StartMenu")
$SunyaFolder = Join-Path $StartMenuPath "Programs\SUNYA Networking"

if (-not (Test-Path $SunyaFolder)) {
    New-Item -ItemType Directory -Path $SunyaFolder -Force | Out-Null
}

$StartShortcutPath = Join-Path $SunyaFolder "$ShortcutName.lnk"
$StartShortcut = $WshShell.CreateShortcut($StartShortcutPath)
$StartShortcut.TargetPath = $ScriptPath
$StartShortcut.WorkingDirectory = $WorkingDirectory
$StartShortcut.Description = "SUNYA Networking Ultimate Automation Suite"
$StartShortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,15"
$StartShortcut.Save()

Write-Host ""
Write-Host "Start Menu shortcut also created!" -ForegroundColor Green
Write-Host "Location: $SunyaFolder"
Write-Host ""

# Cleanup
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($WshShell) | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
