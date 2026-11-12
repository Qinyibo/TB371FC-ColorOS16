@echo off
echo 只在 fastboot 驱动缺失时使用。先阅读 drivers\驱动说明.md。
echo 仅选择平板的 bootloader fastboot 接口，不能选择键盘、鼠标或 USB 集线器。
start "" "%~dp0drivers\zadig-2.9.exe"
set result=%errorlevel%
pause
exit /b %result%
