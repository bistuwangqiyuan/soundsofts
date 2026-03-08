"""Vercel 后端 API 测试 — 对 api/index.py 的 FastAPI 应用进行请求测试."""

import sys
from pathlib import Path

# 使 api.index 可导入（项目根在 path 中）
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pytest
from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)


class TestHealth:
    def test_get_api_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pe-coupling-analyzer"
        assert "version" in data


class TestApiInfo:
    def test_get_api(self):
        r = client.get("/api")
        assert r.status_code == 200
        data = r.json()
        assert data["service"] == "聚乙烯粘接声力耦合分析系统 V1.0"
        assert "endpoints" in data

    def test_get_api_trailing_slash(self):
        r = client.get("/api/")
        assert r.status_code == 200


class TestAnalyze:
    def test_analyze_ok(self):
        waveforms = [[0.1, -0.2, 0.15] * 100, [0.05, 0.1, -0.1] * 100]
        r = client.post("/api/analyze", json={"waveforms": waveforms})
        assert r.status_code == 200
        data = r.json()
        assert data["processed_count"] == 2
        assert len(data["predictions"]) == 2
        assert "mean_force" in data
        assert "features_shape" in data

    def test_analyze_empty_waveforms_400(self):
        r = client.post("/api/analyze", json={"waveforms": []})
        assert r.status_code == 400


class TestReport:
    def test_report_ok(self):
        r = client.post(
            "/api/report",
            json={"specimen_id": "PE-001", "predictions": [72.5, 68.3, 75.0]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["specimen_id"] == "PE-001"
        assert data["prediction_count"] == 3
        assert data["mean_force"] == 71.93  # (72.5 + 68.3 + 75) / 3
        assert data["min_force"] == 68.3
        assert data["max_force"] == 75.0
        assert data["quality"] in ("合格", "不合格")
        assert "summary" in data
        assert "std_force" in data

    def test_report_empty_predictions_400(self):
        r = client.post("/api/report", json={"specimen_id": "X", "predictions": []})
        assert r.status_code == 400


class TestFeatures:
    def test_features_ok(self):
        waveforms = [[0.1, -0.2, 0.15] * 100]
        r = client.post("/api/features", json={"waveforms": waveforms})
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 1
        assert "features_shape" in data
        assert "features" in data
        assert len(data["features"]) == 1

    def test_features_empty_400(self):
        r = client.post("/api/features", json={"waveforms": []})
        assert r.status_code == 400


class TestPredict:
    def test_predict_ok(self):
        features = [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [1.1, 2.1, 3.1, 4.1, 5.1, 6.1]]
        r = client.post("/api/predict", json={"features": features})
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 2
        assert len(data["predictions"]) == 2
        assert "mean_force" in data

    def test_predict_empty_400(self):
        r = client.post("/api/predict", json={"features": []})
        assert r.status_code == 400


class TestAnalyzeReportFlow:
    """前端典型流程：先 analyze 再 report."""

    def test_analyze_then_report(self):
        waveforms = [[0.2, 0.1, -0.1] * 200 for _ in range(3)]
        r1 = client.post("/api/analyze", json={"waveforms": waveforms})
        assert r1.status_code == 200
        predictions = r1.json()["predictions"]

        r2 = client.post(
            "/api/report",
            json={"specimen_id": "FLOW-001", "predictions": predictions},
        )
        assert r2.status_code == 200
        rep = r2.json()
        assert rep["prediction_count"] == 3
        assert rep["specimen_id"] == "FLOW-001"
