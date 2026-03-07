"""聚乙烯粘接声力耦合分析系统 V1.0 — GUI 启动入口（用于打包为可执行文件）."""

from __future__ import annotations

import sys
from pathlib import Path

# 开发时：确保 src 在路径中；打包后：PyInstaller 已配置好路径
if not getattr(sys, "frozen", False):
    _src = Path(__file__).resolve().parent
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))


def main() -> None:
    """启动 GUI 应用."""
    from PySide6.QtWidgets import QApplication
    from gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("聚乙烯粘接声力耦合分析系统 V1.0")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
