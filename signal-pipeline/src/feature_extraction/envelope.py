"""Hilbert-transform envelope extraction with moving-average smoothing."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import hilbert

from ..pipeline.step import PipelineStep


class EnvelopeExtractor(PipelineStep):
    """Compute the amplitude envelope of the signal.

    Args:
        smooth_window: Moving-average window length (0 = no smoothing).
    """

    def __init__(self, smooth_window: int = 5) -> None:
        super().__init__(name="EnvelopeExtractor")
        self.smooth_window = smooth_window

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        analytic = hilbert(signal)
        envelope = np.abs(analytic).astype(signal.dtype)

        if self.smooth_window > 1:
            kernel = np.ones(self.smooth_window) / self.smooth_window
            envelope = np.convolve(envelope, kernel, mode="same").astype(signal.dtype)

        ctx["envelope"] = envelope
        return envelope
