"""Export scikit-learn models to ONNX format via skl2onnx."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


def export_sklearn_to_onnx(
    sklearn_model: object,
    n_features: int,
    output_path: str | Path,
    model_name: str = "model",
) -> None:
    """Convert a fitted sklearn estimator to ONNX and save."""
    initial_type = [("input", FloatTensorType([None, n_features]))]
    onnx_model = convert_sklearn(sklearn_model, initial_types=initial_type, target_opset=17)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
