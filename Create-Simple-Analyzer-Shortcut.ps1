# ==============================================================================
# SUNYA Simple Desktop Analyzer - Shortcut Creator
# ==============================================================================
# Creates a desktop shortcut for the simple analyzer tool
# ==============================================================================

$ErrorActionPreference = "Stop"

# Get paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "SUNYA Simple Analyzer.lnk"
$TargetPath = Join-Path $ScriptDir "SUNYA-Simple-Analyzer.bat"

# Colors
$Green = "Green"
$Cyan = "Cyan"
$Yellow = "Yellow"
$Red = "Red"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
Write-Host "║                                                                            ║" -ForegroundColor $Cyan
Write-Host "║         🌐 SUNYA SIMPLE ANALYZER - SHORTCUT CREATOR 🌐                     ║" -ForegroundColor $Cyan
Write-Host "║                                                                            ║" -ForegroundColor $Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
Write-Host ""

# Check if target exists
if (-not (Test-Path $TargetPath)) {
    Write-Host "[ERROR] SUNYA-Simple-Analyzer.bat not found!" -ForegroundColor $Red
    Write-Host "Expected at: $TargetPath" -ForegroundColor $Yellow
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
    $Shortcut.Description = "SUNYA Simple Desktop Analyzer - One click system analysis"
    $Shortcut.IconLocation = "shell32.dll,14"  # Computer icon
    $Shortcut.WindowStyle = 1
    
    $Shortcut.Save()
    
    Write-Host "[SUCCESS] Desktop shortcut created!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "Shortcut details:" -ForegroundColor $Cyan
    Write-Host "  Name: SUNYA Simple Analyzer.lnk" -ForegroundColor $Green
    Write-Host "  Location: $DesktopPath" -ForegroundColor $Green
    Write-Host ""
    Write-Host "You can now double-click the shortcut on your Desktop to launch the analyzer." -ForegroundColor $Cyan
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to create shortcut: $_" -ForegroundColor $Red
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Sleep -Seconds 2
