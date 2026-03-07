# -*- mode: python ; coding: utf-8 -*-
# 聚乙烯粘接声力耦合分析系统 — PyInstaller 打包配置

import sys
from pathlib import Path

block_cipher = None

# 项目路径
project_root = Path(SPECPATH)
src_path = project_root / 'src'

a = Analysis(
    [str(src_path / 'run_gui.py')],
    pathex=[str(src_path)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'core',
        'core.data_loader',
        'core.preprocessor',
        'core.feature_engine',
        'core.predictor',
        'core.reporter',
        'core.model_loader',
        'core.segmentor',
        'gui',
        'gui.main_window',
        'gui.data_panel',
        'gui.analysis_panel',
        'gui.result_panel',
        'gui.export_dialog',
        'numpy',
        'pandas',
        'scipy',
        'scipy.signal',
        'scipy.fft',
        'h5py',
        'onnxruntime',
        'docx',
        'docx.document',
        'docx.shared',
        'docx.enum.text',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'tensorflow', 'keras', 'pytest', 'IPython', 'jupyter',
        'tkinter', 'unittest',
    ],
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
    name='聚乙烯粘接声力耦合分析系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口，点击即启动 GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
