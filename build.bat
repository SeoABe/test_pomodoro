@echo off
REM ============================================================
REM  Pomodoro single-exe build (size optimized)
REM  Output: dist\pomodoro.exe  (about 12MB, no console window)
REM
REM  Optimizations:
REM   - exclude unused heavy packages (numpy/openblas ~12MB, ssl/crypto ~5MB)
REM   - exclude unused PIL codec (_avif)
REM   - UPX compression (used automatically if present)
REM ============================================================

python -m pip install pyinstaller pystray Pillow

REM Use UPX if it exists under _tools (otherwise skipped)
set "UPX="
if exist "_tools\upx-4.2.4-win64\upx.exe" set "UPX=--upx-dir "_tools\upx-4.2.4-win64" --upx-exclude vcruntime140.dll"

python -m PyInstaller --noconfirm --onefile --windowed --name pomodoro ^
  --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib ^
  --exclude-module pytest --exclude-module setuptools --exclude-module pip ^
  --exclude-module PIL.ImageQt --exclude-module PIL._avif ^
  --exclude-module PyQt5 --exclude-module PySide2 --exclude-module PySide6 ^
  --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib ^
  --exclude-module sqlite3 --exclude-module _sqlite3 ^
  %UPX% ^
  pomodoro.py

echo.
echo Done: dist\pomodoro.exe
pause
