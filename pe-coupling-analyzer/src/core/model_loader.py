"""Load ONNX models for inference."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort


class ONNXModelLoader:
    """Load and run inference with ONNX models."""

    def __init__(self, model_path: str | Path) -> None:
        self.model_path = Path(model_path)
        self.session = ort.InferenceSession(
            str(self.model_path),
            providers=["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, features: np.ndarray) -> np.ndarray:
        X = features.astype(np.float32)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        result = self.session.run(None, {self.input_name: X})
        return np.array(result[0]).flatten()
