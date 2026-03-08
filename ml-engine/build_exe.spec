# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for S2 ML Engine GUI

import sys

block_cipher = None

# 收集所有需要的模块
hiddenimports = [
    "numpy",
    "sklearn",
    "sklearn.ensemble",
    "sklearn.linear_model",
    "sklearn.svm",
    "sklearn.metrics",
    "xgboost",
    "lightgbm",
    "torch",
    "src.models",
    "src.models.linear_regression",
    "src.models.svr_model",
    "src.models.random_forest",
    "src.models.xgboost_model",
    "src.models.lightgbm_model",
    "src.models.cnn_1d",
    "src.utils.metrics",
    "src.data.dataset",
]

a = Analysis(
    ["run_gui.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="S2_ML_Engine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
