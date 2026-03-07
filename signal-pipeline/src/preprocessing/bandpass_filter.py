"""4th-order Butterworth bandpass filter (default 2-8 MHz)."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import butter, sosfiltfilt

from ..pipeline.step import PipelineStep


class BandpassFilter(PipelineStep):
    """Apply a zero-phase Butterworth bandpass filter.

    Args:
        low: Lower cutoff frequency in Hz.
        high: Upper cutoff frequency in Hz.
        fs: Sampling frequency in Hz.
        order: Filter order (default 4).
    """

    def __init__(
        self,
        low: float = 2e6,
        high: float = 8e6,
        fs: float = 40e6,
        order: int = 4,
    ) -> None:
        super().__init__(name="BandpassFilter")
        self.low = low
        self.high = high
        self.fs = fs
        self.order = order
        self._sos = butter(order, [low, high], btype="band", fs=fs, output="sos")

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        fs = ctx.get("sampling_rate", self.fs)
        if fs != self.fs:
            self._sos = butter(self.order, [self.low, self.high], btype="band", fs=fs, output="sos")
            self.fs = fs
        return sosfiltfilt(self._sos, signal).astype(signal.dtype)
