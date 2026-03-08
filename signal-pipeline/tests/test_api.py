"""Vercel API 接口测试：与部署在 Vercel 上的 API 行为一致（通过 FastAPI TestClient）."""

import sys
from pathlib import Path

import numpy as np
import pytest

# 与 api/index.py 相同的路径设置，确保能加载 app
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "api"))

from fastapi.testclient import TestClient

from index import app

client = TestClient(app)


@pytest.fixture
def sample_signal():
    """500 点正弦 + 噪声，与前端 demo 一致."""
    n = 500
    fs = 40e6
    t = np.arange(n) / fs
    sig = np.sin(2 * np.pi * 5e6 * t) * 0.8 + np.sin(2 * np.pi * 2e6 * t) * 0.3
    sig += (np.random.rand(n) - 0.5) * 0.4 + 0.2
    return sig.tolist()


class TestHealth:
    def test_health_returns_200(self):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_body(self):
        r = client.get("/api/health")
        data = r.json()
        assert data["status"] == "healthy"
        assert data["service"] == "S4-signal-pipeline"
        assert "version" in data


class TestPreprocess:
    def test_preprocess_returns_200(self, sample_signal):
        r = client.post(
            "/api/preprocess",
            json={"signal": sample_signal, "sampling_rate": 40e6, "steps": ["dc_removal", "bandpass", "normalize"]},
        )
        assert r.status_code == 200

    def test_preprocess_response_shape(self, sample_signal):
        r = client.post(
            "/api/preprocess",
            json={"signal": sample_signal, "sampling_rate": 40e6, "steps": ["dc_removal", "normalize"]},
        )
        assert r.status_code == 200
        data = r.json()
        assert "processed" in data
        assert "length" in data
        assert len(data["processed"]) == data["length"] == len(sample_signal)

    def test_preprocess_normalized_bounded(self, sample_signal):
        r = client.post(
            "/api/preprocess",
            json={"signal": sample_signal, "sampling_rate": 40e6, "steps": ["dc_removal", "normalize"]},
        )
        assert r.status_code == 200
        processed = r.json()["processed"]
        assert max(abs(x) for x in processed) <= 1.0 + 1e-6

    def test_preprocess_empty_signal_validation(self):
        r = client.post("/api/preprocess", json={"signal": [], "sampling_rate": 40e6})
        assert r.status_code == 422


class TestFeatures:
    def test_features_returns_200(self, sample_signal):
        r = client.post(
            "/api/features",
            json={"signal": sample_signal, "sampling_rate": 40e6},
        )
        assert r.status_code == 200

    def test_features_contains_keys(self, sample_signal):
        r = client.post(
            "/api/features",
            json={"signal": sample_signal, "sampling_rate": 40e6},
        )
        assert r.status_code == 200
        data = r.json()
        assert "features" in data
        feats = data["features"]
        assert "rms" in feats or "vpp" in feats
        assert "center_frequency" in feats or "peak_to_peak" in feats


class TestEnvelope:
    def test_envelope_returns_200(self, sample_signal):
        r = client.post(
            "/api/envelope",
            json={"signal": sample_signal, "sampling_rate": 40e6},
        )
        assert r.status_code == 200

    def test_envelope_length_and_non_negative(self, sample_signal):
        r = client.post(
            "/api/envelope",
            json={"signal": sample_signal, "sampling_rate": 40e6},
        )
        assert r.status_code == 200
        data = r.json()
        assert "envelope" in data
        env = data["envelope"]
        assert len(env) == len(sample_signal)
        assert all(x >= 0 for x in env)


class TestOpenAPI:
    def test_openapi_json_returns_200(self):
        r = client.get("/api/openapi.json")
        assert r.status_code == 200

    def test_docs_returns_200(self):
        r = client.get("/api/docs")
        assert r.status_code == 200
