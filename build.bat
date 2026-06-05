@echo off
REM 단일 실행 파일(.exe) 빌드 스크립트
REM 결과물: dist\pomodoro.exe (콘솔창 없이 실행, 트레이+창 동작)

pip install pyinstaller pystray Pillow

pyinstaller --noconfirm --onefile --windowed --name pomodoro pomodoro.py

echo.
echo 완료: dist\pomodoro.exe
pause
