@echo off
chcp 65001 >nul
echo 正在构建 信号处理流水线 可执行文件...
echo.

pip install -r requirements.txt -q
pyinstaller signal_pipeline.spec --noconfirm

if %ERRORLEVEL% equ 0 (
    echo.
    echo 构建完成！可执行文件位于: dist\信号处理流水线.exe
    echo 双击即可运行。
) else (
    echo 构建失败，请检查错误信息。
    exit /b 1
)
