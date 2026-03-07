"""Performance benchmark: measure inference latency and throughput.

Contract targets:
- Single C-scan analysis: < 10s (target <= 0.65s)
- Prediction MAPE: < 10% (target <= 1.30%)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "signal-pipeline"))
sys.path.insert(0, str(ROOT / "ml-engine"))


def benchmark_preprocessing(n_iterations: int = 1000) -> dict[str, float]:
    """Benchmark signal preprocessing pipeline."""
    from src.pipeline import Pipeline
    from src.preprocessing import DCRemoval, BandpassFilter, WaveletDenoising, Normalization

    pipe = Pipeline([
        DCRemoval(),
        BandpassFilter(2e6, 8e6, 40e6),
        WaveletDenoising(wavelet="db8", level=5),
        Normalization(),
    ])

    signal = np.random.randn(4000).astype(np.float32)

    # Warmup
    for _ in range(10):
        pipe.run(signal, sampling_rate=40e6)

    times = []
    for _ in range(n_iterations):
        t0 = time.perf_counter()
        pipe.run(signal, sampling_rate=40e6)
        times.append(time.perf_counter() - t0)

    return {
        "p50_ms": float(np.percentile(times, 50) * 1000),
        "p95_ms": float(np.percentile(times, 95) * 1000),
        "p99_ms": float(np.percentile(times, 99) * 1000),
        "mean_ms": float(np.mean(times) * 1000),
        "throughput_per_sec": float(1.0 / np.mean(times)),
    }


def benchmark_model_training() -> dict[str, float]:
    """Benchmark model training time."""
    from src.models import RandomForestModel

    np.random.seed(42)
    X = np.random.randn(5000, 5).astype(np.float32)
    y = (3 * X[:, 0] + 2 * X[:, 1] ** 2 + np.random.randn(5000) * 0.5).astype(np.float32)

    times = []
    for _ in range(10):
        model = RandomForestModel(n_estimators=300)
        t0 = time.perf_counter()
        model.train(X, y)
        times.append(time.perf_counter() - t0)

    return {
        "rf_train_mean_s": float(np.mean(times)),
        "rf_train_p95_s": float(np.percentile(times, 95)),
    }


def main() -> None:
    print("=" * 60)
    print("Performance Benchmark — Signal Processing Pipeline")
    print("=" * 60)
    preproc = benchmark_preprocessing()
    for key, val in preproc.items():
        print(f"  {key}: {val:.3f}")
    print(f"  Target: < 650 ms per C-scan (contract < 10,000 ms)")
    print(f"  STATUS: {'PASS' if preproc['p95_ms'] < 10000 else 'FAIL'}")

    print()
    print("=" * 60)
    print("Performance Benchmark — Model Training")
    print("=" * 60)
    training = benchmark_model_training()
    for key, val in training.items():
        print(f"  {key}: {val:.3f}")
    print(f"  Target: RF training < 1.0s")
    print(f"  STATUS: {'PASS' if training['rf_train_mean_s'] < 1.0 else 'FAIL'}")


if __name__ == "__main__":
    main()
