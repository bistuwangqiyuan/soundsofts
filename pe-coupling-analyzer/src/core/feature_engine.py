"""Feature extraction from preprocessed signals."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import hilbert
from scipy.fft import rfft, rfftfreq


def extract_features(data: dict[str, Any]) -> np.ndarray:
    """Extract feature matrix from preprocessed waveforms or existing features."""
    if "features" in data:
        return data["features"]

    waveforms = data.get("processed_waveforms", data.get("waveforms", []))
    if not waveforms:
        return np.array([])

    feature_list = []
    for wf in waveforms:
        feats = _extract_single(wf)
        feature_list.append(feats)
    return np.array(feature_list, dtype=np.float32)


def _extract_single(signal: np.ndarray, fs: float = 40e6) -> list[float]:
    """Extract features from a single waveform."""
    feats: list[float] = []

    # Time-domain
    feats.append(float(np.ptp(signal)))  # Vpp
    feats.append(float(np.sqrt(np.mean(signal ** 2))))  # RMS
    feats.append(float(np.argmax(np.abs(signal))))  # TOF

    # Envelope
    envelope = np.abs(hilbert(signal))
    feats.append(float(np.sum(envelope ** 2)))  # Envelope energy

    # Frequency-domain
    fft_vals = rfft(signal)
    power = np.abs(fft_vals) ** 2
    freqs = rfftfreq(len(signal), d=1.0 / fs)
    total_p = np.sum(power)
    if total_p > 1e-30:
        prob = power / total_p
        feats.append(float(np.sum(freqs * prob)))  # Center freq
    else:
        feats.append(0.0)

    return feats
