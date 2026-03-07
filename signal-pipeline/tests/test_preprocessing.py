"""Tests for all preprocessing steps."""

import numpy as np
import pytest

from src.preprocessing import (
    DCRemoval,
    BandpassFilter,
    WaveletDenoising,
    MedianFilter,
    BaselineCorrection,
    Normalization,
)


@pytest.fixture
def noisy_signal():
    np.random.seed(42)
    t = np.linspace(0, 1e-6, 1000)
    clean = np.sin(2 * np.pi * 5e6 * t)
    noise = 0.3 * np.random.randn(len(t))
    return (clean + noise).astype(np.float32)


class TestDCRemoval:
    def test_zero_mean(self, noisy_signal):
        step = DCRemoval()
        result = step.process(noisy_signal)
        assert abs(np.mean(result)) < 1e-6

    def test_preserves_shape(self, noisy_signal):
        result = DCRemoval().process(noisy_signal)
        assert result.shape == noisy_signal.shape


class TestBandpassFilter:
    def test_output_length(self, noisy_signal):
        filt = BandpassFilter(low=2e6, high=8e6, fs=40e6)
        result = filt.process(noisy_signal, {"sampling_rate": 40e6})
        assert len(result) == len(noisy_signal)

    def test_reduces_noise(self, noisy_signal):
        filt = BandpassFilter(low=2e6, high=8e6, fs=40e6)
        result = filt.process(noisy_signal, {"sampling_rate": 40e6})
        assert np.std(result) < np.std(noisy_signal)


class TestWaveletDenoising:
    def test_output_length(self, noisy_signal):
        wd = WaveletDenoising(wavelet="db4", level=3)
        result = wd.process(noisy_signal)
        assert len(result) == len(noisy_signal)


class TestMedianFilter:
    def test_removes_spikes(self):
        sig = np.zeros(100, dtype=np.float32)
        sig[50] = 100.0
        result = MedianFilter(kernel_size=5).process(sig)
        assert result[50] < 10.0


class TestBaselineCorrection:
    def test_removes_linear_drift(self):
        x = np.arange(500, dtype=np.float32)
        sig = 0.01 * x + np.sin(2 * np.pi * 10 * x / 500)
        result = BaselineCorrection(degree=1).process(sig)
        assert abs(np.mean(result)) < abs(np.mean(sig))


class TestNormalization:
    def test_peak_normalization(self):
        sig = np.array([2.0, -4.0, 3.0], dtype=np.float32)
        result = Normalization(method="peak").process(sig)
        assert np.max(np.abs(result)) == pytest.approx(1.0)

    def test_zscore_normalization(self):
        sig = np.random.randn(200).astype(np.float32)
        result = Normalization(method="zscore").process(sig)
        assert abs(np.mean(result)) < 0.1
        assert abs(np.std(result) - 1.0) < 0.1
