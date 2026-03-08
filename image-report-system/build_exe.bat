@echo off
REM Build executable for 超声图像检测与报告生成系统
REM Requires: pip install pyinstaller

echo Installing PyInstaller...
pip install pyinstaller -q

echo Building executable...
pyinstaller --clean --noconfirm build.spec

echo Done. Executable: dist\ImageReportSystem.exe
