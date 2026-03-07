"""Analysis control panel with parameter settings."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QProgressBar, QTextEdit,
)

import numpy as np


class AnalysisPanel(QWidget):
    """Panel for configuring and running analysis."""

    def __init__(self) -> None:
        super().__init__()
        self._results: dict[str, Any] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Model selection
        model_group = QGroupBox("模型选择")
        model_layout = QFormLayout(model_group)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "随机森林 (Random Forest)",
            "XGBoost",
            "LightGBM",
            "支持向量回归 (SVR)",
            "线性回归",
            "1D-CNN",
        ])
        model_layout.addRow("回归模型:", self.model_combo)
        layout.addWidget(model_group)

        # Preprocessing parameters
        preproc_group = QGroupBox("预处理参数")
        preproc_layout = QFormLayout(preproc_group)

        self.lowcut_spin = QDoubleSpinBox()
        self.lowcut_spin.setRange(0.1, 10.0)
        self.lowcut_spin.setValue(2.0)
        self.lowcut_spin.setSuffix(" MHz")
        preproc_layout.addRow("低截止频率:", self.lowcut_spin)

        self.highcut_spin = QDoubleSpinBox()
        self.highcut_spin.setRange(1.0, 20.0)
        self.highcut_spin.setValue(8.0)
        self.highcut_spin.setSuffix(" MHz")
        preproc_layout.addRow("高截止频率:", self.highcut_spin)

        self.wavelet_level = QSpinBox()
        self.wavelet_level.setRange(1, 10)
        self.wavelet_level.setValue(5)
        preproc_layout.addRow("小波分解层数:", self.wavelet_level)

        layout.addWidget(preproc_group)

        # Run button and progress
        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("开始分析")
        self.run_btn.clicked.connect(lambda: self.run_analysis({}))
        run_layout.addWidget(self.run_btn)
        layout.addLayout(run_layout)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

        layout.addStretch()

    def run_analysis(self, data: dict[str, Any]) -> None:
        self.progress.setValue(0)
        self.log_text.clear()

        self.log_text.append("开始分析...")
        self.progress.setValue(20)

        self.log_text.append(f"使用模型: {self.model_combo.currentText()}")
        self.log_text.append(f"带通滤波: {self.lowcut_spin.value()}-{self.highcut_spin.value()} MHz")
        self.progress.setValue(50)

        # Placeholder for actual analysis
        self._results = {
            "model": self.model_combo.currentText(),
            "predictions": np.random.randn(10).tolist(),
            "metrics": {"MAE": 0.93, "RMSE": 2.17, "R2": 0.9956, "MAPE": 1.30},
        }

        self.progress.setValue(100)
        self.log_text.append("分析完成。")

    def get_results(self) -> dict[str, Any]:
        return self._results
