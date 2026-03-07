"""Standard / MinMax scaling wrappers with serialization."""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class FeatureScaler:
    """Unified scaler that wraps sklearn transformers."""

    def __init__(self, method: str = "standard") -> None:
        if method == "minmax":
            self._scaler = MinMaxScaler()
        else:
            self._scaler = StandardScaler()

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self._scaler.fit_transform(X)

    def transform(self, X: np.ndarray) -> np.ndarray:
        return self._scaler.transform(X)

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self._scaler, f)

    def load(self, path: str | Path) -> None:
        with open(path, "rb") as f:
            self._scaler = pickle.load(f)
