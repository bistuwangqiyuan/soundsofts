"""Tests for core analysis modules."""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core.data_loader import load_data
from core.preprocessor import preprocess_signals
from core.feature_engine import extract_features
from core.predictor import predict_force
from core.reporter import generate_report


class TestDataLoader:
    def test_load_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            df = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0], "force": [80.0, 90.0]})
            df.to_csv(f.name, index=False)
            path = f.name
        try:
            data = load_data(path)
            assert "features" in data
            assert "force" in data
            assert data["features"].shape[0] == 2
            assert data["features"].shape[1] == 2
            assert list(data["force"]) == [80.0, 90.0]
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_csv_no_force(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            df = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0]})
            df.to_csv(f.name, index=False)
            path = f.name
        try:
            data = load_data(path)
            assert "features" in data
            assert len(data["force"]) == 0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            load_data("dummy.txt")

    def test_load_hdf5(self):
        import h5py
        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
            path = f.name
        try:
            with h5py.File(path, "w") as hf:
                g = hf.create_group("spec1")
                g1 = g.create_group("point1")
                g1["waveform"] = np.random.randn(1000).astype(np.float32)
                g1["force"] = 85.0
                g2 = g.create_group("point2")
                g2["waveform"] = np.random.randn(1000).astype(np.float32)
                g2["force"] = 90.0
            data = load_data(path)
            assert "waveforms" in data
            assert len(data["waveforms"]) == 2
            assert len(data["force"]) == 2
        finally:
            Path(path).unlink(missing_ok=True)


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
            generate_report({"source": "test.csv"}, [80.0, 85.0, 90.0], output_path=output)
            assert output.exists()
            assert output.stat().st_size > 0


class TestCLIPipeline:
    """Integration test for full CLI pipeline."""

    def test_full_pipeline_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            df = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0], "force": [80.0, 90.0]})
            df.to_csv(csv_path, index=False)
            out_path = Path(tmpdir) / "report.docx"

            # Simulate CLI run
            data = load_data(csv_path)
            processed = preprocess_signals(data)
            features = extract_features(processed)
            predictions = predict_force(features, model_path="nonexistent.onnx")
            generate_report(data, predictions, output_path=out_path)

            assert out_path.exists()
            assert len(predictions) == 2
