"""Polynomial baseline correction."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..pipeline.step import PipelineStep


class BaselineCorrection(PipelineStep):
    """Fit and subtract a polynomial baseline.

    Args:
        degree: Polynomial degree (default 3).
    """

    def __init__(self, degree: int = 3) -> None:
        super().__init__(name="BaselineCorrection")
        self.degree = degree

    def process(self, signal: np.ndarray, ctx: dict[str, Any] | None = None) -> np.ndarray:
        x = np.arange(len(signal), dtype=np.float64)
        coeffs = np.polyfit(x, signal, self.degree)
        baseline = np.polyval(coeffs, x)
        return (signal - baseline).astype(signal.dtype)
