"""Signal preprocessing wrapper."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import butter, sosfiltfilt


def preprocess_signals(data: dict[str, Any]) -> dict[str, Any]:
    """Apply preprocessing to signal data."""
    result = dict(data)

    if "waveforms" in data:
        processed = []
        for wf in data["waveforms"]:
            clean = _remove_dc(wf)
            clean = _bandpass(clean, low=2e6, high=8e6, fs=40e6)
            clean = _normalize(clean)
            processed.append(clean)
        result["processed_waveforms"] = processed

    return result


def _remove_dc(signal: np.ndarray) -> np.ndarray:
    return signal - np.mean(signal)


def _bandpass(signal: np.ndarray, low: float, high: float, fs: float) -> np.ndarray:
    sos = butter(4, [low, high], btype="band", fs=fs, output="sos")
    return sosfiltfilt(sos, signal).astype(signal.dtype)


def _normalize(signal: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(signal))
    if peak < 1e-12:
        return signal
    return signal / peak
