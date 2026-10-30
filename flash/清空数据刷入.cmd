@echo off
echo 将清空平板全部用户数据。请确认备份，仅连接目标 TB371FC，并进入 bootloader fastboot。
set "confirm="
set /p confirm=请输入 FLASH 继续：
if /I not "%confirm%"=="FLASH" exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Invoke-R91-Clean.ps1" -Execute -Clean -Reboot
set result=%errorlevel%
pause
exit /b %result%
