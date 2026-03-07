"""Tests for quality control utilities."""

import tempfile
from pathlib import Path

import numpy as np

from src.quality import SNRCalculator, OutlierDetector, HashVerifier, QualityReportGenerator


class TestSNR:
    def test_high_snr(self):
        waveform = np.zeros(1000, dtype=np.float32)
        waveform[100:300] = 1.0
        calc = SNRCalculator(signal_window=(100, 300), noise_window=(600, 900))
        snr = calc.compute(waveform)
        assert snr > 20


class TestOutlierDetector:
    def test_iqr_detects_outlier(self):
        values = np.array([1, 2, 3, 2, 1, 100], dtype=np.float32)
        det = OutlierDetector(method="iqr", threshold=1.5)
        mask = det.detect(values)
        assert mask[-1]

    def test_clip(self):
        values = np.array([1, 2, 3, 2, 1, 100], dtype=np.float32)
        det = OutlierDetector()
        clipped = det.clip(values)
        assert clipped[-1] < 100


class TestHashVerifier:
    def test_compute_and_verify(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"test data for hashing")
            path = f.name
        h = HashVerifier.compute(path)
        assert HashVerifier.verify(path, h)
        assert not HashVerifier.verify(path, "wrong_hash")
        Path(path).unlink()
