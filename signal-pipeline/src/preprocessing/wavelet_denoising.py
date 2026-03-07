"""Daubechies-8 wavelet threshold denoising with Minimax threshold."""

from __future__ import annotations

from typing import Any

import numpy as np
import pywt

from ..pipeline.step import PipelineStep


class WaveletDenoising(PipelineStep):
    """Wavelet-based denoising using soft thresholding.

    Args:
        wavelet: Wavelet family (default ``db8``).
        level: Decomposition depth (default 5).
        threshold_mode: ``'soft'`` or ``'hard'``.
    """

    def __init__(
        self,
        wavelet: str = "db8",
        level: int = 5,
        threshold_mode: str = "soft",
    ) -> None:
        super().__init__(name="WaveletDenoising")
        self.wavelet = wavelet
        self.level = level
        self.threshold_mode = threshold_mode

    def _minimax_threshold(self, n: int, sigma: float) -> float:
        """Minimax threshold: σ · (0.3936 + 0.1829 · log2(n))."""
        if n < 32:
            return sigma * 0.3936
        return sigma * (0.3936 + 0.1829 * np.log2(n))

    def process(self, signal: np.ndarray, **ctx: Any) -> np.ndarray:
        coeffs = pywt.wavedec(signal, self.wavelet, level=self.level)

        # Estimate noise σ from finest detail coefficients (MAD estimator)
        detail_finest = coeffs[-1]
        sigma = float(np.median(np.abs(detail_finest)) / 0.6745)

        thresholded = [coeffs[0]]  # keep approximation coefficients
        for detail in coeffs[1:]:
            thr = self._minimax_threshold(len(detail), sigma)
            thresholded.append(pywt.threshold(detail, value=thr, mode=self.threshold_mode))

        return pywt.waverec(thresholded, self.wavelet)[: len(signal)].astype(signal.dtype)
