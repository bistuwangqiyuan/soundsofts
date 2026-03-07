"""Cross-system integration tests.

Verify data flows correctly between S4→S2→S5→S7.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "signal-pipeline"))
sys.path.insert(0, str(ROOT / "pe-coupling-analyzer" / "src"))


def _switch_src(project: str):
    """Clear cached ``src`` package and repoint sys.path to *project*."""
    for key in list(sys.modules):
        if key == "src" or key.startswith("src."):
            del sys.modules[key]
    proj = str(ROOT / project)
    if proj in sys.path:
        sys.path.remove(proj)
    sys.path.insert(0, proj)


class TestS4ToS2:
    """S4 signal pipeline → S2 ML engine data flow."""

    def test_feature_matrix_compatible(self):
        """Features extracted by S4 are consumable by S2 models."""
        _switch_src("signal-pipeline")
        from src.pipeline import Pipeline
        from src.preprocessing import DCRemoval, BandpassFilter, Normalization
        from src.feature_extraction import TimeDomainFeatures, FrequencyDomainFeatures

        np.random.seed(42)
        signals = [np.random.randn(1000).astype(np.float32) for _ in range(10)]

        pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, 40e6), Normalization()])

        all_features = []
        for sig in signals:
            processed = pipe.run(sig, sampling_rate=40e6)
            ctx: dict = {"sampling_rate": 40e6}
            TimeDomainFeatures().process(processed, ctx)
            FrequencyDomainFeatures().process(processed, ctx)
            all_features.append(list(ctx["features"].values()))

        feature_matrix = np.array(all_features, dtype=np.float32)
        assert feature_matrix.shape[0] == 10
        assert feature_matrix.shape[1] > 5
        assert not np.any(np.isnan(feature_matrix))
        assert not np.any(np.isinf(feature_matrix))


class TestS5ReportGeneration:
    """S5 image report system integration."""

    def test_rule_engine(self):
        _switch_src("image-report-system")
        from src.multimodal_fusion.rule_engine import RuleEngine

        engine = RuleEngine()
        checks = engine.run_all_checks(force=85.0, defect_area=100, total_area=10000)

        assert len(checks) == 2
        assert checks[0].passed  # 85 > 70 N/cm
        assert checks[1].passed  # 1% < 5%

    def test_fusion_result(self):
        _switch_src("image-report-system")
        from src.multimodal_fusion.fusion import fuse_results
        from src.multimodal_fusion.rule_engine import RuleCheckResult

        mask = np.zeros((100, 100), dtype=np.float32)
        checks = [RuleCheckResult(passed=True, rule_name="test", message="ok")]

        result = fuse_results(mask, 0.9, 85.0, checks)
        assert result.overall_quality == "合格"
        assert result.confidence > 0.5


class TestS7Standalone:
    """S7 standalone analyzer integration."""

    def test_full_cli_pipeline(self):
        from core.preprocessor import preprocess_signals
        from core.feature_engine import extract_features
        from core.predictor import predict_force

        data = {"waveforms": [np.random.randn(1000).astype(np.float32) for _ in range(5)]}
        processed = preprocess_signals(data)
        features = extract_features(processed)
        predictions = predict_force(features)

        assert len(predictions) == 5
        assert all(np.isfinite(predictions))
