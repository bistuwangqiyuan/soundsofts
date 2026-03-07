"""Median filter for spike / impulse noise removal."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.ndimage import median_filter as _medfilt

from ..pipeline.step import PipelineStep


class MedianFilter(PipelineStep):
    """1-D median filter with configurable kernel size."""

    def __init__(self, kernel_size: int = 5) -> None:
        super().__init__(name="MedianFilter")
        self.kernel_size = kernel_size

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        return _medfilt(signal, size=self.kernel_size).astype(signal.dtype)
