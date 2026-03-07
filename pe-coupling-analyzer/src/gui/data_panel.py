"""Data import and preview panel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QGroupBox,
)

from core.data_loader import load_data


class DataPanel(QWidget):
    """Panel for loading and previewing CSV/HDF5 data."""

    def __init__(self) -> None:
        super().__init__()
        self._data: dict[str, Any] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        ctrl = QHBoxLayout()
        self.load_btn = QPushButton("加载文件")
        self.load_btn.clicked.connect(self._on_load)
        ctrl.addWidget(self.load_btn)

        self.file_label = QLabel("未加载文件")
        ctrl.addWidget(self.file_label)
        ctrl.addStretch()

        self.info_label = QLabel("")
        ctrl.addWidget(self.info_label)
        layout.addLayout(ctrl)

        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout(preview_group)
        self.table = QTableWidget()
        preview_layout.addWidget(self.table)
        layout.addWidget(preview_group)

    def _on_load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", "", "CSV文件 (*.csv);;HDF5文件 (*.hdf5 *.h5);;所有文件 (*)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str) -> None:
        try:
            self._data = load_data(path)
        except Exception as e:
            self.file_label.setText("加载失败")
            self.info_label.setText(str(e))
            self._data = {}
            self._update_table()
            return

        p = Path(path)
        self.file_label.setText(p.name)

        if "dataframe" in self._data:
            df = self._data["dataframe"]
            self.info_label.setText(f"{len(df)} 行 × {len(df.columns)} 列")
        elif "waveforms" in self._data:
            n = len(self._data["waveforms"])
            self.info_label.setText(f"{n} 个测点 (HDF5)")
        else:
            self.info_label.setText("已加载")

        self._update_table()

    def _update_table(self) -> None:
        if not self._data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        if "dataframe" in self._data:
            import pandas as pd
            df = self._data["dataframe"]
            df_preview = df.head(100)
            self.table.setRowCount(len(df_preview))
            self.table.setColumnCount(len(df.columns))
            self.table.setHorizontalHeaderLabels(list(df.columns))
            for i in range(len(df_preview)):
                for j in range(len(df.columns)):
                    self.table.setItem(i, j, QTableWidgetItem(str(df_preview.iloc[i, j])))
        elif "waveforms" in self._data:
            waveforms = self._data["waveforms"]
            forces = self._data.get("force", [])
            n = min(len(waveforms), 100)
            self.table.setRowCount(n)
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["序号", "波形长度", "力值 (N)"])
            for i in range(n):
                self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.table.setItem(i, 1, QTableWidgetItem(str(len(waveforms[i]))))
                f = forces[i] if i < len(forces) else ""
                self.table.setItem(i, 2, QTableWidgetItem(str(f)))
        else:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)

    def get_data(self) -> dict[str, Any]:
        return self._data
