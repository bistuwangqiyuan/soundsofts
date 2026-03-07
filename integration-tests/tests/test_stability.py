"""Stability tests: memory leak detection and continuous operation."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "signal-pipeline"))


class TestMemoryStability:
    """Detect memory leaks in signal processing pipeline."""

    def test_no_memory_leak_preprocessing(self):
        """Run preprocessing 1000 times and verify no significant memory growth."""
        import psutil

        from src.pipeline import Pipeline
        from src.preprocessing import DCRemoval, BandpassFilter, Normalization

        pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])
        signal = np.random.randn(4000).astype(np.float32)

        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        for _ in range(1000):
            pipe.run(signal, sampling_rate=40e6)

        mem_after = process.memory_info().rss / 1024 / 1024
        mem_growth = mem_after - mem_before

        assert mem_growth < 50, f"Memory grew by {mem_growth:.1f} MB over 1000 iterations"


class TestDataConsistency:
    """Verify data processing produces consistent results."""

    def test_deterministic_output(self):
        """Same input → same output across multiple runs."""
        from src.pipeline import Pipeline
        from src.preprocessing import DCRemoval, BandpassFilter, Normalization

        pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])
        signal = np.random.RandomState(42).randn(2000).astype(np.float32)

        results = [pipe.run(signal.copy(), sampling_rate=40e6) for _ in range(10)]

        for r in results[1:]:
            np.testing.assert_array_almost_equal(results[0], r, decimal=6)
