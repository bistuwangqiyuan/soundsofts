"""Signal preprocessing service - calls signal-pipeline when available."""

import asyncio
from typing import Any, Optional

import numpy as np

from core.config import get_settings

settings = get_settings()


class SignalProcessorService:
    """Process signals through preprocessing pipeline (DC removal, bandpass, denoise)."""

    def __init__(self) -> None:
        self._pipeline = None

    def _get_pipeline(
        self,
        bandpass_low: float,
        bandpass_high: float,
        sampling_rate: float,
        dc_removal: bool,
        denoise: bool,
    ):
        """Build pipeline from signal-pipeline if available."""
        try:
            import sys
            from pathlib import Path
            # Add signal-pipeline to path if in sibling directory
            root = Path(__file__).resolve().parents[3]  # soundsofts
            sp_path = root / "signal-pipeline" / "src"
            if sp_path.exists() and str(sp_path) not in sys.path:
                sys.path.insert(0, str(sp_path))
            from pipeline.pipeline import Pipeline
            from preprocessing.dc_removal import DCRemoval
            from preprocessing.bandpass_filter import BandpassFilter  # noqa: F401
        except ImportError:
            return None

        steps = []
        if dc_removal:
            steps.append(DCRemoval())
        steps.append(
            BandpassFilter(
                low=bandpass_low,
                high=bandpass_high,
                fs=sampling_rate,
            )
        )
        if denoise:
            try:
                from signal_pipeline.preprocessing.wavelet_denoising import (
                    WaveletDenoising,
                )

                steps.append(WaveletDenoising())
            except ImportError:
                pass
        return Pipeline(steps) if steps else None

    async def process(
        self,
        signal: list[float],
        sampling_rate: float = 40e6,
        bandpass_low: float = 2e6,
        bandpass_high: float = 8e6,
        dc_removal: bool = True,
        denoise: bool = False,
    ) -> dict[str, Any]:
        """Process signal and optionally extract features."""
        arr = np.array(signal, dtype=np.float64)
        pipeline = self._get_pipeline(
            bandpass_low, bandpass_high, sampling_rate, dc_removal, denoise
        )
        if pipeline:
            processed = await asyncio.to_thread(
                pipeline.run, arr, sampling_rate=sampling_rate
            )
        else:
            processed = self._fallback_process(arr, sampling_rate, bandpass_low, bandpass_high, dc_removal)
        features = await asyncio.to_thread(
            self._extract_features, processed, sampling_rate
        )
        return {
            "processed": processed.tolist(),
            "features": features,
        }

    def _fallback_process(
        self,
        arr: np.ndarray,
        fs: float,
        low: float,
        high: float,
        dc_removal: bool,
    ) -> np.ndarray:
        """Fallback processing when signal-pipeline is not installed."""
        out = arr.copy()
        if dc_removal:
            out = out - np.mean(out)
        # Simple FFT-based bandpass
        n = len(out)
        fft = np.fft.rfft(out)
        freqs = np.fft.rfftfreq(n, 1 / fs)
        mask = (freqs >= low) & (freqs <= high)
        fft[~mask] = 0
        out = np.fft.irfft(fft, n)
        return out.astype(np.float64)

    def _extract_features(self, signal: np.ndarray, fs: float) -> dict[str, float]:
        """Extract basic time/domain features."""
        n = len(signal)
        return {
            "rms": float(np.sqrt(np.mean(signal**2))),
            "peak_to_peak": float(np.ptp(signal)),
            "mean": float(np.mean(signal)),
        }
