"""Unified feature extraction across time, frequency, and time-frequency domains."""

from __future__ import annotations

import numpy as np
from scipy.signal import hilbert
from scipy.fft import rfft, rfftfreq


def extract_all_features(signal: np.ndarray, fs: float = 40e6) -> dict[str, float]:
    """Extract a comprehensive feature vector from one A-scan waveform."""
    feats: dict[str, float] = {}

    # Time-domain
    feats["vpp"] = float(np.ptp(signal))
    feats["rms"] = float(np.sqrt(np.mean(signal ** 2)))
    feats["tof"] = float(np.argmax(np.abs(signal)))
    mean_abs = float(np.mean(np.abs(signal)))
    feats["waveform_factor"] = feats["rms"] / mean_abs if mean_abs > 1e-12 else 0.0
    feats["crest_factor"] = float(np.max(np.abs(signal))) / feats["rms"] if feats["rms"] > 1e-12 else 0.0
    sign_changes = np.diff(np.sign(signal))
    feats["zcr"] = float(np.count_nonzero(sign_changes) / len(signal))

    # Envelope
    envelope = np.abs(hilbert(signal))
    feats["envelope_energy"] = float(np.sum(envelope ** 2))
    half_max = np.max(envelope) / 2
    above = np.where(envelope >= half_max)[0]
    feats["fwhm"] = float(above[-1] - above[0]) if len(above) > 1 else 0.0

    # Frequency-domain
    n = len(signal)
    fft_vals = rfft(signal)
    power = np.abs(fft_vals) ** 2
    freqs = rfftfreq(n, d=1.0 / fs)
    total_p = np.sum(power)
    if total_p > 1e-30:
        prob = power / total_p
        feats["center_freq"] = float(np.sum(freqs * prob))
        feats["bandwidth"] = float(np.sqrt(np.sum(((freqs - feats["center_freq"]) ** 2) * prob)))
        pnz = prob[prob > 0]
        ent = float(-np.sum(pnz * np.log2(pnz)))
        feats["spectral_entropy"] = ent / np.log2(len(pnz)) if len(pnz) > 1 else 0.0
    else:
        feats["center_freq"] = 0.0
        feats["bandwidth"] = 0.0
        feats["spectral_entropy"] = 0.0

    return feats
