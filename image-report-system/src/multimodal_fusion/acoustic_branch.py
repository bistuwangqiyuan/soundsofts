"""Acoustic-force coupling branch using Random Forest ONNX model."""

from __future__ import annotations

import numpy as np
import onnxruntime as ort


class AcousticBranch:
    """Quantitative bonding force prediction via RF ONNX model."""

    def __init__(self, model_path: str) -> None:
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name

    def predict_force(self, features: np.ndarray) -> np.ndarray:
        """Predict bonding force from acoustic features."""
        X = features.astype(np.float32)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        result = self.session.run(None, {self.input_name: X})
        return np.array(result[0]).flatten()
