"""Remove DC offset from ultrasonic waveform."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..pipeline.step import PipelineStep


class DCRemoval(PipelineStep):
    """Subtract the mean value (DC component) from the signal."""

    def __init__(self) -> None:
        super().__init__(name="DCRemoval")

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        return signal - np.mean(signal)
