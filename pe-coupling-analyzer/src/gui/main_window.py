"""Main application window with tabbed interface."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMenuBar, QMenu, QToolBar,
    QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from .data_panel import DataPanel
from .analysis_panel import AnalysisPanel
from .result_panel import ResultPanel


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("聚乙烯粘接声力耦合分析系统 V1.0")
        self.setMinimumSize(1200, 800)

        self._setup_menu()
        self._setup_toolbar()
        self._setup_tabs()
        self._setup_statusbar()

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件(&F)")
        open_action = QAction("打开数据(&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        export_action = QAction("导出报告(&E)...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)

        file_menu.addSeparator()
        quit_action = QAction("退出(&Q)", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = menubar.addMenu("帮助(&H)")
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        open_btn = QAction("打开", self)
        open_btn.triggered.connect(self._on_open)
        toolbar.addAction(open_btn)

        analyze_btn = QAction("开始分析", self)
        analyze_btn.triggered.connect(self._on_analyze)
        toolbar.addAction(analyze_btn)

        export_btn = QAction("导出报告", self)
        export_btn.triggered.connect(self._on_export)
        toolbar.addAction(export_btn)

    def _setup_tabs(self) -> None:
        self.tabs = QTabWidget()
        self.data_panel = DataPanel()
        self.analysis_panel = AnalysisPanel()
        self.result_panel = ResultPanel()

        self.tabs.addTab(self.data_panel, "数据导入")
        self.tabs.addTab(self.analysis_panel, "分析控制")
        self.tabs.addTab(self.result_panel, "结果展示")

        self.setCentralWidget(self.tabs)

    def _setup_statusbar(self) -> None:
        self.statusBar().showMessage("就绪")

    def _on_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "打开数据文件", "", "数据文件 (*.csv *.hdf5 *.h5);;所有文件 (*)"
        )
        if path:
            self.data_panel.load_file(path)
            self.statusBar().showMessage(f"已加载: {path}")

    def _on_analyze(self) -> None:
        self.statusBar().showMessage("分析中...")
        self.analysis_panel.run_analysis(self.data_panel.get_data())
        self.result_panel.update_results(self.analysis_panel.get_results())
        self.tabs.setCurrentIndex(2)
        self.statusBar().showMessage("分析完成")

    def _on_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "导出报告", "report.docx", "Word文档 (*.docx)"
        )
        if path:
            self.result_panel.export_report(path)
            self.statusBar().showMessage(f"报告已导出: {path}")

    def _on_about(self) -> None:
        QMessageBox.about(
            self, "关于",
            "聚乙烯粘接声力耦合分析系统 V1.0\n\n"
            "开发单位：北京信息科技大学\n"
            "软件著作权登记号：2026SR0XXXXXX\n"
            "版本：V1.0\n"
            "日期：2026年1月"
        )
