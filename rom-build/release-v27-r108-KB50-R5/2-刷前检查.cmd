@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Invoke-R91-Clean.ps1" -CheckDevice
set result=%errorlevel%
pause
exit /b %result%
