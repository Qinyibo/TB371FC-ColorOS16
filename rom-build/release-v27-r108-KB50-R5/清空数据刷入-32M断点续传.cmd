@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo TB371FC v27-r108-KB50-R5 wipe flash with 32MiB sparse parts + checkpoint resume
echo Device must be in bootloader fastboot. This ERASES userdata.
echo Progress: super-parts-progress.json (next_index). Re-run this cmd to resume.
set /p confirm=Type FLASH to continue: 
if /I not "%confirm%"=="FLASH" exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Invoke-R91-Clean.ps1" -Execute -Clean -Reboot
set result=%errorlevel%
pause
exit /b %result%
