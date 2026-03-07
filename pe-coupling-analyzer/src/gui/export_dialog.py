"""Export configuration dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QGroupBox, QFormLayout, QCheckBox, QDialogButtonBox,
)


class ExportDialog(QDialog):
    """Dialog for configuring report export options."""

    def __init__(self, parent: object = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("导出设置")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        settings_group = QGroupBox("报告设置")
        form = QFormLayout(settings_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["Word (.docx)", "CSV (.csv)"])
        form.addRow("导出格式:", self.format_combo)

        self.include_charts = QCheckBox("包含图表")
        self.include_charts.setChecked(True)
        form.addRow(self.include_charts)

        self.include_raw_data = QCheckBox("包含原始数据")
        form.addRow(self.include_raw_data)

        layout.addWidget(settings_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
