"""Tests for backend API (local or Vercel). Set API_BASE_URL for deployed API."""

from __future__ import annotations

import os
import pytest
import requests

# Default: local server. For Vercel: export API_BASE_URL=https://xxx.vercel.app
API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")


def _url(path: str) -> str:
    return API_BASE.rstrip("/") + path


@pytest.fixture(scope="module")
def base_url():
    return API_BASE.rstrip("/")


class TestHealth:
    def test_health_returns_200(self, base_url):
        r = requests.get(_url("/api/health"), timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "healthy"
        assert "S3" in data.get("service", "") or "unet" in data.get("service", "").lower()

    def test_health_json(self, base_url):
        r = requests.get(_url("/api/health"), timeout=10)
        assert r.headers.get("content-type", "").startswith("application/json")


class TestMetrics:
    def test_metrics_returns_200(self, base_url):
        r = requests.get(_url("/api/metrics"), timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "IoU" in data
        assert "Dice" in data

    def test_metrics_values(self, base_url):
        r = requests.get(_url("/api/metrics"), timeout=10)
        data = r.json()
        assert isinstance(data["IoU"], (int, float))
        assert isinstance(data["Dice"], (int, float))


class TestArchitecture:
    def test_architecture_returns_200(self, base_url):
        r = requests.get(_url("/api/architecture"), timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "model" in data
        assert "U-Net" in data.get("model", "")


class TestSimulate:
    def test_simulate_post_returns_200(self, base_url):
        r = requests.post(
            _url("/api/simulate"),
            json={"width": 80, "height": 60, "defect_count": 2},
            timeout=10,
        )
        assert r.status_code == 200
        data = r.json()
        assert "image" in data
        assert "pred_mask" in data
        assert "iou" in data
        assert "dice" in data
        assert data["defect_count"] == 2

    def test_simulate_validation(self, base_url):
        # Invalid: width too small
        r = requests.post(
            _url("/api/simulate"),
            json={"width": 10, "height": 60, "defect_count": 0},
            timeout=10,
        )
        assert r.status_code == 422
