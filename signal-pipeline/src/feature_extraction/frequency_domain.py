"""Frequency-domain feature extraction via FFT."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..pipeline.step import PipelineStep


class FrequencyDomainFeatures(PipelineStep):
    """Extract spectral features using the FFT.

    Computed features (stored in ``ctx['features']``):
    - ``center_frequency``: spectral centroid
    - ``bandwidth``: spectral bandwidth (standard deviation of freq)
    - ``spectral_entropy``: normalized entropy of power spectrum
    - ``spectral_moment_2``, ``spectral_moment_3``: 2nd and 3rd spectral moments
    """

    def __init__(self) -> None:
        super().__init__(name="FrequencyDomainFeatures")

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        fs: float = ctx.get("sampling_rate", 40e6)
        n = len(signal)

        fft_vals = np.fft.rfft(signal)
        power = np.abs(fft_vals) ** 2
        freqs = np.fft.rfftfreq(n, d=1.0 / fs)

        total_power = np.sum(power)
        if total_power < 1e-30:
            ctx.setdefault("features", {}).update({
                "center_frequency": 0.0,
                "bandwidth": 0.0,
                "spectral_entropy": 0.0,
                "spectral_moment_2": 0.0,
                "spectral_moment_3": 0.0,
            })
            return signal

        prob = power / total_power
        center_freq = float(np.sum(freqs * prob))
        variance = float(np.sum(((freqs - center_freq) ** 2) * prob))
        bandwidth = float(np.sqrt(variance))

        # Spectral entropy (normalized)
        prob_nonzero = prob[prob > 0]
        entropy = float(-np.sum(prob_nonzero * np.log2(prob_nonzero)))
        max_entropy = np.log2(len(prob_nonzero)) if len(prob_nonzero) > 1 else 1.0
        spectral_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        moment_3 = float(np.sum(((freqs - center_freq) ** 3) * prob))

        features = {
            "center_frequency": center_freq,
            "bandwidth": bandwidth,
            "spectral_entropy": spectral_entropy,
            "spectral_moment_2": variance,
            "spectral_moment_3": moment_3,
        }
        ctx.setdefault("features", {}).update(features)
        return signal
