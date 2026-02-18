@echo off
REM 使用当前 Python 环境，用 PyInstaller 打包库存管理系统
REM 运行前请确认已在虚拟环境中安装了 pyinstaller

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Building InOutInventory.exe ...
pyinstaller in_out.spec

echo.
echo 打包完成，如果成功，可以在 dist\InOutInventory\ 或 dist\InOutInventory.exe 中找到可执行文件。
pause

