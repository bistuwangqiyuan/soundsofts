"""Performance tests for pipeline throughput."""

import time

import numpy as np
import pytest

from src.pipeline import Pipeline
from src.preprocessing import DCRemoval, BandpassFilter, Normalization


def test_throughput_500_points_per_sec():
    """Pipeline must achieve >= 500 points/sec throughput."""
    pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])
    np.random.seed(0)
    # Use 5000 points to get stable timing
    sig = np.random.randn(5000).astype(np.float32)
    ctx = {"sampling_rate": 40e6}

    # Warm-up run
    pipe.run(sig, ctx=ctx)

    # Timed runs
    n_runs = 10
    total_points = 0
    t0 = time.perf_counter()
    for _ in range(n_runs):
        pipe.run(sig, ctx=ctx)
        total_points += len(sig)
    elapsed = time.perf_counter() - t0

    throughput = total_points / elapsed
    assert throughput >= 500, f"Throughput {throughput:.0f} pts/s < 500 pts/s target"
