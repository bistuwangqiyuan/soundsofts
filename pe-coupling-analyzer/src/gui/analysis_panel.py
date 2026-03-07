"""Analysis control panel with parameter settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QProgressBar, QTextEdit, QMessageBox,
)

import numpy as np

from core.preprocessor import preprocess_signals
from core.feature_engine import extract_features
from core.predictor import predict_force


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
        self._data_provider = lambda: {}
        self.run_btn.clicked.connect(self._on_run_clicked)
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

    def set_data_provider(self, provider) -> None:
        """Set callback to get data from DataPanel."""
        self._data_provider = provider

    def _on_run_clicked(self) -> None:
        self.run_analysis(self._data_provider())

    def run_analysis(self, data: dict[str, Any]) -> None:
        self.progress.setValue(0)
        self.log_text.clear()

        if not data or (not data.get("waveforms") and not data.get("features")):
            self.log_text.append("请先在「数据导入」标签页加载数据文件。")
            QMessageBox.warning(self, "提示", "请先加载 CSV 或 HDF5 数据文件。")
            return

        self.log_text.append("开始分析...")
        self.progress.setValue(10)

        try:
            self.log_text.append("预处理信号...")
            processed = preprocess_signals(data)
            self.progress.setValue(30)

            self.log_text.append("提取特征...")
            features = extract_features(processed)
            self.progress.setValue(50)

            if features.size == 0:
                self.log_text.append("错误：未能提取到有效特征。")
                return

            model_path = Path(__file__).resolve().parent.parent.parent / "resources" / "models" / "random_forest.onnx"
            self.log_text.append(f"预测粘接力 (模型: {self.model_combo.currentText()})...")
            predictions = predict_force(features, model_path=str(model_path))
            self.progress.setValue(80)

            # Compute metrics if ground truth available
            forces = data.get("force", np.array([]))
            metrics: dict[str, float] = {}
            if len(forces) > 0 and len(forces) == len(predictions):
                preds = np.asarray(predictions)
                acts = np.asarray(forces)
                metrics["MAE"] = float(np.mean(np.abs(preds - acts)))
                metrics["RMSE"] = float(np.sqrt(np.mean((preds - acts) ** 2)))
                ss_res = np.sum((acts - preds) ** 2)
                ss_tot = np.sum((acts - np.mean(acts)) ** 2)
                metrics["R2"] = float(1 - ss_res / ss_tot) if ss_tot > 1e-12 else 0.0
                mape = np.mean(np.abs((acts - preds) / (acts + 1e-12))) * 100
                metrics["MAPE"] = float(mape)

            self._results = {
                "model": self.model_combo.currentText(),
                "predictions": predictions.tolist() if hasattr(predictions, "tolist") else list(predictions),
                "metrics": metrics or {"MAE": 0, "RMSE": 0, "R2": 0, "MAPE": 0},
                "data": data,
            }

            self.progress.setValue(100)
            self.log_text.append(f"分析完成。共 {len(predictions)} 个预测点。")
        except Exception as e:
            self.log_text.append(f"分析失败: {e}")
            QMessageBox.critical(self, "错误", str(e))

    def get_results(self) -> dict[str, Any]:
        return self._results
