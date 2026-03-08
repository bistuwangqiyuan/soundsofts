@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在安装/更新 PyInstaller ...
pip install -q pyinstaller h5py numpy pandas
echo 正在打包可执行文件 ...
pyinstaller -y build_exe.spec
if %ERRORLEVEL% equ 0 (
    echo.
    echo 打包完成。可执行文件位置: dist\LabVIEW_B_S_Acquisition.exe
    echo 双击 exe 即可运行软件 GUI。
) else (
    echo 打包失败，请检查错误信息。
    exit /b 1
)
