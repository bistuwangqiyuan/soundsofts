"""Abstract base class for all regression models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import numpy as np


class BaseModel(ABC):
    """Unified interface: train / predict / evaluate / export."""

    name: str = "BaseModel"

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> None:
        ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        ...

    @abstractmethod
    def get_params(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def save(self, path: str | Path) -> None:
        ...

    @abstractmethod
    def load(self, path: str | Path) -> None:
        ...

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        from ..utils.metrics import compute_metrics
        preds = self.predict(X)
        return compute_metrics(y, preds)
