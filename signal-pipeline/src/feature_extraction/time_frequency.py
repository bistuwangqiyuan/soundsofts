"""Time-frequency analysis via STFT (Hanning) and CWT (Morlet)."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import stft as _stft

from ..pipeline.step import PipelineStep


class TimeFrequencyFeatures(PipelineStep):
    """Compute STFT and CWT statistics.

    Features stored in ``ctx['features']``:
    - ``stft_peak_energy``: max energy in STFT spectrogram
    - ``stft_mean_energy``: mean energy of STFT spectrogram
    - ``stft_energy_std``: standard deviation of STFT energy
    - ``cwt_peak_scale``: CWT scale with maximum energy
    """

    def __init__(self, nperseg: int = 128) -> None:
        super().__init__(name="TimeFrequencyFeatures")
        self.nperseg = nperseg

    def process(self, signal: np.ndarray, ctx: dict[str, Any] | None = None) -> np.ndarray:
        ctx = ctx if ctx is not None else {}
        fs: float = ctx.get("sampling_rate", 40e6)
        features: dict[str, float] = {}

        # STFT with Hanning window
        _, _, zxx = _stft(signal, fs=fs, window="hann", nperseg=min(self.nperseg, len(signal)))
        energy = np.abs(zxx) ** 2
        features["stft_peak_energy"] = float(np.max(energy))
        features["stft_mean_energy"] = float(np.mean(energy))
        features["stft_energy_std"] = float(np.std(energy))

        # CWT with Morlet wavelet (scales 1..32)
        import pywt
        max_scale = min(32, len(signal) // 4) or 1
        scales = np.arange(1, max_scale + 1)
        coeffs, _ = pywt.cwt(signal, scales, "morl", sampling_period=1.0 / fs)
        cwt_energy = np.sum(np.abs(coeffs) ** 2, axis=1)
        features["cwt_peak_scale"] = float(scales[np.argmax(cwt_energy)])

        ctx.setdefault("features", {}).update(features)
        return signal
