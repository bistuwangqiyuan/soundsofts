"""Build GUI launcher executable with PyInstaller. Run from project root: python scripts/build_exe.py"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    try:
        import PyInstaller
    except ImportError:
        print("请先安装 PyInstaller: pip install pyinstaller")
        sys.exit(1)
    subprocess.run(
        [
            sys.executable,
            "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(ROOT / "build_exe.spec"),
        ],
        cwd=str(ROOT),
        check=True,
    )
    exe_dir = ROOT / "dist"
    print(f"构建完成。可执行文件在: {exe_dir}")


if __name__ == "__main__":
    main()
