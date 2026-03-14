"""Tests for API endpoints (local FastAPI TestClient)."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from api.index import app

client = TestClient(app)


class TestHealth:
    def test_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "2.0" in data["version"]


class TestRoot:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "service" in data
        assert "endpoints" in data


class TestAnalyze:
    def test_analyze_pass(self):
        r = client.post("/api/analyze", json={"force": 85.0, "defect_area": 100, "total_area": 10000})
        assert r.status_code == 200
        data = r.json()
        assert "checks" in data
        assert "all_passed" in data
        assert len(data["checks"]) == 5

    def test_analyze_fail(self):
        r = client.post("/api/analyze", json={"force": 50.0, "defect_area": 600, "total_area": 10000})
        assert r.status_code == 200
        data = r.json()
        assert data["all_passed"] is False


class TestFuse:
    def test_fuse_default(self):
        r = client.post("/api/fuse", json={"predicted_force": 85.0, "defect_ratio": 0.01, "visual_confidence": 0.9})
        assert r.status_code == 200
        data = r.json()
        assert "quality" in data
        assert "confidence" in data
        assert data["quality"] in ("合格", "不合格", "待复核")

    def test_fuse_with_weights(self):
        r = client.post("/api/fuse", json={
            "predicted_force": 85.0, "defect_ratio": 0.01, "visual_confidence": 0.9,
            "w_visual": 0.5, "w_acoustic": 0.3, "w_rules": 0.2,
        })
        assert r.status_code == 200
        data = r.json()
        assert "branch_scores" in data

    def test_fuse_has_branch_scores(self):
        r = client.post("/api/fuse", json={"predicted_force": 85.0, "defect_ratio": 0.01, "visual_confidence": 0.9})
        data = r.json()
        if data.get("branch_scores"):
            assert len(data["branch_scores"]) == 3


class TestAnalyzeFull:
    def test_analyze_full(self):
        r = client.post("/api/analyze-full", json={
            "force": 85.0, "defect_area": 100, "total_area": 10000,
            "visual_confidence": 0.9, "defect_ratio": 0.01,
        })
        assert r.status_code == 200
        data = r.json()
        assert "checks" in data
        assert "quality" in data
        assert "branch_scores" in data


class TestTerminology:
    def test_terminology(self):
        r = client.get("/api/terminology")
        assert r.status_code == 200
        data = r.json()
        assert "terms" in data
        assert isinstance(data["terms"], dict)


class TestDefectTypes:
    def test_defect_types(self):
        r = client.get("/api/defect-types")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 4
        assert all("key" in d and "label" in d for d in data)


class TestStandards:
    def test_standards(self):
        r = client.get("/api/standards")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        assert all("name" in s and "value" in s for s in data)
