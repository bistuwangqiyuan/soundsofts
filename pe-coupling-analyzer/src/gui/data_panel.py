"""Data import and preview panel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QGroupBox,
)

import pandas as pd


class DataPanel(QWidget):
    """Panel for loading and previewing CSV/HDF5 data."""

    def __init__(self) -> None:
        super().__init__()
        self._data: pd.DataFrame | None = None
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
            self, "选择数据文件", "", "CSV文件 (*.csv);;HDF5文件 (*.hdf5 *.h5)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str) -> None:
        p = Path(path)
        if p.suffix == ".csv":
            self._data = pd.read_csv(p)
        elif p.suffix in (".hdf5", ".h5"):
            self._data = pd.read_hdf(p)
        else:
            return

        self.file_label.setText(p.name)
        self.info_label.setText(f"{len(self._data)} 行 × {len(self._data.columns)} 列")
        self._update_table()

    def _update_table(self) -> None:
        if self._data is None:
            return
        df = self._data.head(100)
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(list(df.columns))
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

    def get_data(self) -> dict[str, Any]:
        if self._data is None:
            return {}
        return {"dataframe": self._data}
