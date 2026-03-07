"""Integration tests for the Pipeline orchestrator."""

import numpy as np
import pytest

from src.pipeline import Pipeline
from src.preprocessing import DCRemoval, BandpassFilter, Normalization


def test_pipeline_chain():
    pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])
    np.random.seed(0)
    sig = np.random.randn(1000).astype(np.float32)
    result = pipe.run(sig, sampling_rate=40e6)
    assert result.shape == sig.shape
    assert np.max(np.abs(result)) <= 1.0 + 1e-6


def test_pipeline_batch():
    pipe = Pipeline([DCRemoval(), Normalization()])
    batch = np.random.randn(5, 500).astype(np.float32)
    results = pipe.run_batch(batch)
    assert results.shape == batch.shape


def test_disabled_step():
    dc = DCRemoval()
    dc.enabled = False
    pipe = Pipeline([dc, Normalization()])
    sig = np.ones(100, dtype=np.float32) * 5.0
    result = pipe.run(sig)
    # DC should NOT have been removed; normalization should still work
    assert np.max(np.abs(result)) == pytest.approx(1.0)
