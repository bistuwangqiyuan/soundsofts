"""Signal-to-noise ratio calculator."""

from __future__ import annotations

import numpy as np


class SNRCalculator:
    """Estimate SNR from a windowed signal/noise partition.

    Args:
        signal_window: (start, end) sample indices of the echo region.
        noise_window: (start, end) sample indices of the noise-only region.
    """

    def __init__(
        self,
        signal_window: tuple[int, int] = (100, 300),
        noise_window: tuple[int, int] = (600, 900),
    ) -> None:
        self.signal_window = signal_window
        self.noise_window = noise_window

    def compute(self, waveform: np.ndarray) -> float:
        """Return SNR in dB."""
        sig = waveform[self.signal_window[0]: self.signal_window[1]]
        noise = waveform[self.noise_window[0]: self.noise_window[1]]
        p_sig = float(np.mean(sig ** 2))
        p_noise = float(np.mean(noise ** 2))
        if p_noise < 1e-30:
            return 100.0
        return float(10.0 * np.log10(p_sig / p_noise))
