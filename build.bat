@echo off
REM ─────────────────────────────────────────────────────────────
REM  포모도로 단일 실행 파일(.exe) 빌드 - 용량 최적화 버전
REM  결과물: dist\pomodoro.exe  (약 12MB, 콘솔창 없음)
REM
REM  최적화 포인트:
REM   - 미사용 대용량 패키지 제외 (numpy/openblas 약 12MB, ssl/crypto 약 5MB 등)
REM   - PIL 미사용 코덱(_avif) 제외
REM   - UPX 압축 (있을 때만 자동 적용)
REM ─────────────────────────────────────────────────────────────

pip install pyinstaller pystray Pillow

REM UPX 가 _tools 폴더에 있으면 사용 (없으면 생략됨)
set UPX=
if exist "_tools\upx-4.2.4-win64\upx.exe" set UPX=--upx-dir "_tools\upx-4.2.4-win64" --upx-exclude vcruntime140.dll

pyinstaller --noconfirm --onefile --windowed --name pomodoro ^
  --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib ^
  --exclude-module pytest --exclude-module setuptools --exclude-module pip ^
  --exclude-module PIL.ImageQt --exclude-module PIL._avif ^
  --exclude-module PyQt5 --exclude-module PySide2 --exclude-module PySide6 ^
  --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib ^
  --exclude-module sqlite3 --exclude-module _sqlite3 ^
  %UPX% ^
  pomodoro.py

echo.
echo 완료: dist\pomodoro.exe
pause
