@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Install-Magisk.ps1"
set "result=%errorlevel%"
pause
exit /b %result%
