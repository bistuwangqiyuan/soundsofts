"""Signal amplitude normalization."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..pipeline.step import PipelineStep


class Normalization(PipelineStep):
    """Normalize signal to [-1, 1] range by dividing by peak absolute value.

    Args:
        method: ``'peak'`` (default) or ``'zscore'``.
    """

    def __init__(self, method: str = "peak") -> None:
        super().__init__(name="Normalization")
        self.method = method

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        if self.method == "zscore":
            std = np.std(signal)
            if std < 1e-12:
                return np.zeros_like(signal)
            return ((signal - np.mean(signal)) / std).astype(signal.dtype)

        peak = np.max(np.abs(signal))
        if peak < 1e-12:
            return np.zeros_like(signal)
        return (signal / peak).astype(signal.dtype)
