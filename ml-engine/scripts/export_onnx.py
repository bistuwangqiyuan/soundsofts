"""Export the best sklearn model to ONNX format."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pickle
from src.inference.onnx_exporter import export_sklearn_to_onnx


def main() -> None:
    model_path = Path("models/random_forest.pkl")
    if not model_path.exists():
        print(f"Model not found at {model_path}. Train first with train_all.py")
        return

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    output = Path("models/random_forest.onnx")
    export_sklearn_to_onnx(model, n_features=5, output_path=output)
    print(f"Exported to {output}")


if __name__ == "__main__":
    main()
