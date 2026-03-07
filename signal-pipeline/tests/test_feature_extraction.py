"""Tests for feature extraction modules."""

import numpy as np
import pytest

from src.feature_extraction import TimeDomainFeatures, FrequencyDomainFeatures, EnvelopeExtractor


@pytest.fixture
def sine_signal():
    t = np.linspace(0, 1e-6, 2000)
    return np.sin(2 * np.pi * 5e6 * t).astype(np.float32)


class TestTimeDomain:
    def test_extracts_features(self, sine_signal):
        ctx: dict = {}
        TimeDomainFeatures().process(sine_signal, **ctx)
        assert "vpp" in ctx["features"]
        assert "rms" in ctx["features"]
        assert ctx["features"]["vpp"] > 0

    def test_zero_crossing_rate(self, sine_signal):
        ctx: dict = {}
        TimeDomainFeatures().process(sine_signal, **ctx)
        assert ctx["features"]["zero_crossing_rate"] > 0


class TestFrequencyDomain:
    def test_center_frequency(self, sine_signal):
        ctx: dict = {"sampling_rate": 40e6}
        FrequencyDomainFeatures().process(sine_signal, **ctx)
        cf = ctx["features"]["center_frequency"]
        assert 4e6 < cf < 6e6

    def test_spectral_entropy_bounded(self, sine_signal):
        ctx: dict = {"sampling_rate": 40e6}
        FrequencyDomainFeatures().process(sine_signal, **ctx)
        assert 0 <= ctx["features"]["spectral_entropy"] <= 1.0


class TestEnvelope:
    def test_envelope_positive(self, sine_signal):
        ctx: dict = {}
        env = EnvelopeExtractor(smooth_window=0).process(sine_signal, **ctx)
        assert np.all(env >= 0)

    def test_envelope_in_ctx(self, sine_signal):
        ctx: dict = {}
        EnvelopeExtractor().process(sine_signal, **ctx)
        assert "envelope" in ctx
