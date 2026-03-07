@echo off
chcp 65001 >nul
echo ========================================
echo 聚乙烯粘接声力耦合分析系统 - 打包为可执行文件
echo ========================================
echo.

REM 检查依赖
python -c "import PyInstaller" 2>nul || (
    echo 请先安装依赖: pip install -r requirements.txt
    pause
    exit /b 1
)

echo 正在打包...
pyinstaller --noconfirm --clean pe_analyzer.spec

if %ERRORLEVEL% equ 0 (
    echo.
    echo 打包完成！
    echo 可执行文件位置: dist\聚乙烯粘接声力耦合分析系统.exe
    echo 双击该文件即可运行 GUI。
) else (
    echo 打包失败。
)

pause
