"""A/B testing support for comparing model versions in production."""

from __future__ import annotations

import random
from typing import Any

import numpy as np

from ..models.base_model import BaseModel


class ABTest:
    """Route inference requests between two model versions."""

    def __init__(self, model_a: BaseModel, model_b: BaseModel, traffic_ratio: float = 0.5) -> None:
        self.model_a = model_a
        self.model_b = model_b
        self.ratio = traffic_ratio
        self.log: list[dict[str, Any]] = []

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, str]:
        """Return (predictions, variant_name)."""
        if random.random() < self.ratio:
            return self.model_a.predict(X), "A"
        return self.model_b.predict(X), "B"
