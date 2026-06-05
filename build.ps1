# Pomodoro single-exe build (size optimized) - PowerShell version
# Output: dist\pomodoro.exe  (about 12MB, no console window)
#
# Usage:  powershell -ExecutionPolicy Bypass -File build.ps1
#   or right-click build.ps1 -> Run with PowerShell

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

python -m pip install pyinstaller pystray Pillow

# Use UPX automatically if present under _tools
$upx = @()
if (Test-Path "_tools\upx-4.2.4-win64\upx.exe") {
    $upx = @("--upx-dir", "_tools\upx-4.2.4-win64", "--upx-exclude", "vcruntime140.dll")
}

python -m PyInstaller --noconfirm --onefile --windowed --name pomodoro `
  --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib `
  --exclude-module pytest --exclude-module setuptools --exclude-module pip `
  --exclude-module PIL.ImageQt --exclude-module PIL._avif `
  --exclude-module PyQt5 --exclude-module PySide2 --exclude-module PySide6 `
  --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib `
  --exclude-module sqlite3 --exclude-module _sqlite3 `
  @upx `
  pomodoro.py

Write-Host ""
Write-Host "Done: dist\pomodoro.exe" -ForegroundColor Green
