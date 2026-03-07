"""Unified inference interface for ONNX and native models."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort


class ONNXPredictor:
    """Run inference using ONNX Runtime."""

    def __init__(self, model_path: str | Path) -> None:
        self.session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, X: np.ndarray) -> np.ndarray:
        X_float = X.astype(np.float32)
        result = self.session.run(None, {self.input_name: X_float})
        return np.array(result[0]).flatten()
