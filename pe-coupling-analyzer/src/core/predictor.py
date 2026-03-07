"""Bonding force prediction using ONNX models."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .model_loader import ONNXModelLoader


def predict_force(
    features: np.ndarray,
    model_path: str | Path = "resources/models/random_forest.onnx",
) -> np.ndarray:
    """Predict bonding force from feature matrix."""
    if not Path(model_path).exists():
        # Fallback: simple linear prediction for demo
        if features.size == 0:
            return np.array([])
        return np.mean(features, axis=1) * 10 + 50

    model = ONNXModelLoader(model_path)
    return model.predict(features)
