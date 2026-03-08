"""Tests for API endpoints (local FastAPI TestClient)."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

# Import app - api/index adds src to path for multimodal_fusion etc.
from api.index import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "S5" in data["service"]


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "service" in data


def test_analyze():
    r = client.post(
        "/api/analyze",
        json={"force": 85.0, "defect_area": 100, "total_area": 10000},
    )
    assert r.status_code == 200
    data = r.json()
    assert "checks" in data
    assert "all_passed" in data
    assert len(data["checks"]) >= 1


def test_analyze_fail():
    r = client.post(
        "/api/analyze",
        json={"force": 50.0, "defect_area": 600, "total_area": 10000},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["all_passed"] is False


def test_fuse():
    r = client.post(
        "/api/fuse",
        json={"predicted_force": 85.0, "defect_ratio": 0.01, "visual_confidence": 0.9},
    )
    assert r.status_code == 200
    data = r.json()
    assert "quality" in data
    assert "confidence" in data
    assert data["quality"] in ("合格", "不合格", "待复核")


def test_terminology():
    r = client.get("/api/terminology")
    assert r.status_code == 200
    data = r.json()
    assert "terms" in data
    assert isinstance(data["terms"], dict)
