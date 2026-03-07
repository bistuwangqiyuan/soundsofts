# -*- mode: python ; coding: utf-8 -*-
# S4 数据预处理与信号处理流水线 — PyInstaller 打包配置

import sys
from pathlib import Path

block_cipher = None

project_root = Path(SPECPATH)
public_dir = project_root / "public"
api_dir = project_root / "api"
src_dir = project_root / "src"

# 需要打包的数据文件
datas = [
    (str(public_dir), "public"),
    (str(api_dir / "index.py"), "api"),
    (str(src_dir), "src"),
]

# 收集 src 下所有 Python 模块（用于 hiddenimports）
hiddenimports = [
    "pipeline",
    "pipeline.pipeline",
    "pipeline.step",
    "pipeline.config",
    "preprocessing",
    "preprocessing.dc_removal",
    "preprocessing.bandpass_filter",
    "preprocessing.wavelet_denoising",
    "preprocessing.median_filter",
    "preprocessing.baseline_correction",
    "preprocessing.normalization",
    "preprocessing.frame_alignment",
    "feature_extraction",
    "feature_extraction.time_domain",
    "feature_extraction.frequency_domain",
    "feature_extraction.envelope",
    "feature_extraction.regional_stats",
    "feature_extraction.time_frequency",
    "numpy",
    "scipy",
    "scipy.signal",
    "scipy.fft",
    "pandas",
    "pywt",
    "h5py",
    "fastapi",
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
]

a = Analysis(
    [str(project_root / "run_gui.py")],
    pathex=[str(project_root), str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch", "matplotlib", "pytest", "IPython", "tkinter",
        "PIL", "cv2", "sklearn.tests", "pandas.tests",
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
    name="信号处理流水线",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台，点击即启动 GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
