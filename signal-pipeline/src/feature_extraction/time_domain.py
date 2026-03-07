"""Time-domain feature extraction for A-scan waveforms."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..pipeline.step import PipelineStep


class TimeDomainFeatures(PipelineStep):
    """Extract time-domain features and attach them to context.

    Computed features (stored in ``ctx['features_td']``):
    - ``vpp``: peak-to-peak voltage
    - ``tof``: time of flight (index of max absolute value)
    - ``envelope_energy``: sum of squared envelope
    - ``fwhm``: full width at half maximum of envelope
    - ``zero_crossing_rate``: zero-crossing rate
    - ``waveform_factor``: RMS / mean(|signal|)
    - ``rms``: root mean square amplitude
    - ``crest_factor``: peak / RMS
    """

    def __init__(self) -> None:
        super().__init__(name="TimeDomainFeatures")

    def process(self, signal: np.ndarray, ctx: dict[str, Any] | None = None) -> np.ndarray:
        ctx = ctx if ctx is not None else {}
        features: dict[str, float] = {}

        features["vpp"] = float(np.ptp(signal))
        features["tof"] = float(np.argmax(np.abs(signal)))

        rms = float(np.sqrt(np.mean(signal ** 2)))
        features["rms"] = rms
        features["crest_factor"] = float(np.max(np.abs(signal)) / rms) if rms > 1e-12 else 0.0

        mean_abs = float(np.mean(np.abs(signal)))
        features["waveform_factor"] = rms / mean_abs if mean_abs > 1e-12 else 0.0

        # Zero-crossing rate
        sign_changes = np.diff(np.sign(signal))
        features["zero_crossing_rate"] = float(np.count_nonzero(sign_changes) / len(signal))

        # Envelope via analytic signal (lightweight)
        from scipy.signal import hilbert
        envelope = np.abs(hilbert(signal))
        features["envelope_energy"] = float(np.sum(envelope ** 2))

        # FWHM of envelope
        half_max = np.max(envelope) / 2
        above = envelope >= half_max
        if np.any(above):
            indices = np.where(above)[0]
            features["fwhm"] = float(indices[-1] - indices[0])
        else:
            features["fwhm"] = 0.0

        ctx.setdefault("features", {}).update(features)
        return signal
