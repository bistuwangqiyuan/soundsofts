"""Align A-scan frames using cross-correlation with a reference waveform."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import correlate

from ..pipeline.step import PipelineStep


class FrameAlignment(PipelineStep):
    """Shift signal to align with a reference via cross-correlation.

    If no reference is provided in *ctx*, the step is a no-op.
    """

    def __init__(self) -> None:
        super().__init__(name="FrameAlignment")

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        ref: np.ndarray | None = ctx.get("reference_waveform")
        if ref is None:
            return signal

        correlation = correlate(signal, ref, mode="full")
        lag = int(np.argmax(correlation)) - (len(ref) - 1)

        if lag == 0:
            return signal

        aligned = np.zeros_like(signal)
        if lag > 0:
            aligned[:-lag] = signal[lag:]
        else:
            aligned[-lag:] = signal[:lag]
        return aligned
