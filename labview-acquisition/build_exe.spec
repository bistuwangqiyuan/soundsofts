# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: 打包为单文件 exe，点击运行 GUI
# 用法: pyinstaller build_exe.spec  或  build_exe.bat

from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / 'main.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / 'Config'), 'Config'),
        (str(ROOT / 'public'), 'public'),
    ],
    hiddenimports=['python_interface', 'python_interface.data_reader', 'python_interface.tcp_stream', 'python_interface.calibration_manager'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'matplotlib', 'scipy', 'pytest', 'IPython', 'tkinter.test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LabVIEW_B_S_Acquisition',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台，直接显示 GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
