"""Support Vector Regression with RBF kernel."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.svm import SVR

from .base_model import BaseModel


class SVRModel(BaseModel):
    name = "SVR"

    def __init__(self, C: float = 1.0, epsilon: float = 0.1, kernel: str = "rbf", **kwargs: Any) -> None:
        self.model = SVR(C=C, epsilon=epsilon, kernel=kernel, **kwargs)

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def get_params(self) -> dict[str, Any]:
        return self.model.get_params()

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path: str | Path) -> None:
        with open(path, "rb") as f:
            self.model = pickle.load(f)
