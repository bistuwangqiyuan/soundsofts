"""Tests for core analysis modules."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from core.preprocessor import preprocess_signals
from core.feature_engine import extract_features
from core.predictor import predict_force
from core.reporter import generate_report


class TestPreprocessor:
    def test_processes_waveforms(self):
        data = {"waveforms": [np.random.randn(1000).astype(np.float32) for _ in range(3)]}
        result = preprocess_signals(data)
        assert "processed_waveforms" in result
        assert len(result["processed_waveforms"]) == 3


class TestFeatureEngine:
    def test_extract_from_waveforms(self):
        data = {"processed_waveforms": [np.random.randn(1000).astype(np.float32) for _ in range(5)]}
        features = extract_features(data)
        assert features.shape[0] == 5
        assert features.shape[1] > 0

    def test_passthrough_existing_features(self):
        features = np.random.randn(10, 5).astype(np.float32)
        data = {"features": features}
        result = extract_features(data)
        assert np.array_equal(result, features)


class TestPredictor:
    def test_fallback_prediction(self):
        features = np.random.randn(5, 3).astype(np.float32)
        preds = predict_force(features, model_path="nonexistent.onnx")
        assert len(preds) == 5


class TestReporter:
    def test_generates_docx(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.docx"
            generate_report({"source": "test.csv"}, [80.0, 85.0, 90.0], output)
            assert output.exists()
            assert output.stat().st_size > 0
