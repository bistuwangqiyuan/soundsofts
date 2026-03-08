@echo off
REM 构建 S2 ML Engine 可执行文件
cd /d "%~dp0.."
pip install pyinstaller -q
pyinstaller build_exe.spec
echo.
echo 可执行文件位于: dist\S2_ML_Engine.exe
pause
