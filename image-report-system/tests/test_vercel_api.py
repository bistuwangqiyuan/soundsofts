"""Tests for Vercel-deployed API. Run with: BASE_URL=https://xxx.vercel.app pytest tests/test_vercel_api.py -v"""

import os

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
# Skip unless BASE_URL is set (use BASE_URL=https://your-app.vercel.app for deployed API)
SKIP_VERCEL = not BASE_URL


@pytest.fixture(scope="module")
def base_url():
    return BASE_URL or "http://localhost:3000"


@pytest.mark.skipif(SKIP_VERCEL, reason="Set BASE_URL to deployed Vercel URL to run (e.g. BASE_URL=https://xxx.vercel.app)")
def test_vercel_health(base_url):
    r = requests.get(f"{base_url}/api/health", timeout=10)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data.get("status") == "healthy"


@pytest.mark.skipif(SKIP_VERCEL, reason="Set BASE_URL to deployed Vercel URL to run")
def test_vercel_analyze(base_url):
    r = requests.post(
        f"{base_url}/api/analyze",
        json={"force": 85.0, "defect_area": 100, "total_area": 10000},
        timeout=10,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "checks" in data
    assert "all_passed" in data


@pytest.mark.skipif(SKIP_VERCEL, reason="Set BASE_URL to deployed Vercel URL to run")
def test_vercel_fuse(base_url):
    r = requests.post(
        f"{base_url}/api/fuse",
        json={"predicted_force": 85.0, "defect_ratio": 0.01, "visual_confidence": 0.9},
        timeout=10,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "quality" in data
    assert data["quality"] in ("合格", "不合格", "待复核")


@pytest.mark.skipif(SKIP_VERCEL, reason="Set BASE_URL to deployed Vercel URL to run")
def test_vercel_terminology(base_url):
    r = requests.get(f"{base_url}/api/terminology", timeout=10)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "terms" in data
