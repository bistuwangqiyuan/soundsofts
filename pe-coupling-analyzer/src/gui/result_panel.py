"""Results display and export panel."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem, QTextEdit,
)


class ResultPanel(QWidget):
    """Panel for displaying analysis results and exporting reports."""

    def __init__(self) -> None:
        super().__init__()
        self._results: dict[str, Any] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Metrics summary
        metrics_group = QGroupBox("性能指标")
        metrics_layout = QVBoxLayout(metrics_group)
        self.metrics_table = QTableWidget(4, 2)
        self.metrics_table.setHorizontalHeaderLabels(["指标", "值"])
        self.metrics_table.setMaximumHeight(180)
        metrics_layout.addWidget(self.metrics_table)
        layout.addWidget(metrics_group)

        # Predictions table
        pred_group = QGroupBox("预测结果")
        pred_layout = QVBoxLayout(pred_group)
        self.pred_table = QTableWidget()
        pred_layout.addWidget(self.pred_table)
        layout.addWidget(pred_group)

        # Export buttons
        btn_layout = QHBoxLayout()
        self.export_word_btn = QPushButton("导出Word报告")
        self.export_csv_btn = QPushButton("导出CSV")
        btn_layout.addWidget(self.export_word_btn)
        btn_layout.addWidget(self.export_csv_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def update_results(self, results: dict[str, Any]) -> None:
        self._results = results

        metrics = results.get("metrics", {})
        metrics_list = [
            ("MAE", f"{metrics.get('MAE', 0):.3f}"),
            ("RMSE", f"{metrics.get('RMSE', 0):.3f}"),
            ("R²", f"{metrics.get('R2', 0):.4f}"),
            ("MAPE", f"{metrics.get('MAPE', 0):.2f}%"),
        ]
        self.metrics_table.setRowCount(len(metrics_list))
        for i, (name, val) in enumerate(metrics_list):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(name))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(val))

        predictions = results.get("predictions", [])
        self.pred_table.setRowCount(len(predictions))
        self.pred_table.setColumnCount(2)
        self.pred_table.setHorizontalHeaderLabels(["序号", "预测力值 (N)"])
        for i, p in enumerate(predictions):
            self.pred_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.pred_table.setItem(i, 1, QTableWidgetItem(f"{p:.2f}"))

    def export_report(self, path: str) -> None:
        from core.reporter import generate_report
        data = self._results.get("data", {})
        if not data:
            data = {"source": "GUI 分析"}
        generate_report(data, self._results.get("predictions", []), output_path=path)
