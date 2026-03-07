"""End-to-end pipeline integration tests.

Validates the full flow: raw data → preprocessing → feature extraction →
model prediction → report generation.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

# Add system paths
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "signal-pipeline"))
sys.path.insert(0, str(ROOT / "ml-engine"))
sys.path.insert(0, str(ROOT / "pe-coupling-analyzer" / "src"))


class TestFullPipeline:
    """Test the complete analysis pipeline end-to-end."""

    def test_signal_preprocessing_chain(self):
        """S4 → Verify preprocessing pipeline produces valid output."""
        from src.pipeline import Pipeline
        from src.preprocessing import DCRemoval, BandpassFilter, Normalization

        pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])
        np.random.seed(42)
        signal = np.random.randn(2000).astype(np.float32)

        result = pipe.run(signal, sampling_rate=40e6)

        assert result.shape == signal.shape
        assert np.max(np.abs(result)) <= 1.0 + 1e-5
        assert abs(np.mean(result)) < 0.1

    def test_feature_extraction(self):
        """S4 → Verify feature extraction produces expected number of features."""
        from src.feature_extraction import TimeDomainFeatures, FrequencyDomainFeatures

        signal = np.sin(2 * np.pi * 5e6 * np.linspace(0, 1e-6, 2000)).astype(np.float32)
        ctx: dict = {"sampling_rate": 40e6}

        TimeDomainFeatures().process(signal, **ctx)
        FrequencyDomainFeatures().process(signal, **ctx)

        features = ctx["features"]
        assert "vpp" in features
        assert "center_frequency" in features
        assert features["vpp"] > 0

    def test_model_training_and_prediction(self):
        """S2 → Verify model can train and predict."""
        from src.models import RandomForestModel
        from src.utils.metrics import compute_metrics

        np.random.seed(42)
        X = np.random.randn(200, 5).astype(np.float32)
        y = (2 * X[:, 0] + X[:, 1] + np.random.randn(200) * 0.1).astype(np.float32)

        model = RandomForestModel(n_estimators=50)
        model.train(X[:150], y[:150])
        preds = model.predict(X[150:])
        metrics = compute_metrics(y[150:], preds)

        assert preds.shape == (50,)
        assert metrics["R2"] > 0.5

    def test_report_generation(self):
        """S7 → Verify report generation produces valid docx."""
        from core.reporter import generate_report

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_report.docx"
            generate_report(
                {"source": "test_data.csv"},
                [80.0, 85.5, 92.3, 77.8, 88.1],
                output_path=output,
            )
            assert output.exists()
            assert output.stat().st_size > 1000

    def test_spatial_alignment(self):
        """S4 → Verify spatial alignment produces aligned data."""
        from src.spatial import SpatialAlignment

        positions = np.arange(0, 50, 1.0)
        timestamps = np.arange(len(positions), dtype=np.float64)
        forces = np.sin(positions / 5.0).astype(np.float32)

        aligner = SpatialAlignment(grid_spacing_mm=1.0)
        grid, aligned = aligner.align(positions, timestamps, positions, timestamps, forces)

        assert len(grid) > 0
        assert len(grid) == len(aligned)

    def test_quality_assessment(self):
        """S4 → Verify quality report generation."""
        from src.quality import QualityReportGenerator

        np.random.seed(42)
        waveforms = np.random.randn(20, 1000).astype(np.float32)
        waveforms[:, 100:300] += 5.0

        gen = QualityReportGenerator()
        metrics = gen.evaluate(waveforms)

        assert metrics.total_points == 20
        assert metrics.valid_points > 0
        assert metrics.mean_snr_db > 0


class TestContractVerification:
    """Verify all contract-specified performance requirements."""

    def test_analysis_speed_target(self):
        """Contract: single C-scan analysis < 10s (target 0.65s)."""
        import time
        from src.pipeline import Pipeline
        from src.preprocessing import DCRemoval, BandpassFilter, Normalization

        pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])
        signal = np.random.randn(4000).astype(np.float32)

        times = []
        for _ in range(100):
            t0 = time.perf_counter()
            pipe.run(signal, sampling_rate=40e6)
            times.append(time.perf_counter() - t0)

        p95 = np.percentile(times, 95)
        assert p95 < 10.0, f"P95 analysis time {p95:.3f}s exceeds 10s contract limit"

    def test_data_integrity(self):
        """Verify data hash verification works correctly."""
        import tempfile
        from src.quality import HashVerifier

        with tempfile.NamedTemporaryFile(delete=False, suffix=".dat") as f:
            f.write(b"test acoustic data integrity check")
            path = f.name

        h = HashVerifier.compute(path)
        assert HashVerifier.verify(path, h)
        assert not HashVerifier.verify(path, "tampered_hash")
        Path(path).unlink()
