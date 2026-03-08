"""API 接口测试（本地 FastAPI 或 Vercel 部署后）。"""

import os
import pytest
import requests

# 优先使用环境变量中的 API 地址（Vercel 部署后）
# 未设置时使用 TestClient，无需启动服务器
BASE_URL = os.environ.get("ML_ENGINE_API_URL", "")


@pytest.fixture(scope="module")
def api_url():
    if BASE_URL:
        return BASE_URL.rstrip("/")
    return None


@pytest.fixture(scope="module")
def client(api_url):
    """使用 TestClient（无需服务器）或 requests（远程 API）。"""
    if api_url:
        return None  # 使用 requests
    from fastapi.testclient import TestClient
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from api.index import app
    return TestClient(app)


class TestHealth:
    def test_health_returns_ok(self, api_url, client):
        if client:
            r = client.get("/api/health")
        else:
            r = requests.get(f"{api_url}/api/health", timeout=10)
        if r.status_code == 401:
            pytest.skip("Vercel 部署保护已启用，请在项目设置中关闭 Deployment Protection 以允许公开访问")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "healthy"
        assert "ml-engine" in data.get("service", "").lower() or "S2" in data.get("service", "")


class TestModels:
    def test_models_list(self, api_url, client):
        if client:
            r = client.get("/api/models")
        else:
            r = requests.get(f"{api_url}/api/models", timeout=10)
        if r.status_code == 401:
            pytest.skip("Vercel 部署保护已启用")
        assert r.status_code == 200
        data = r.json()
        assert "models" in data
        assert len(data["models"]) >= 1
        assert any(m["name"] == "random_forest" for m in data["models"])


class TestTrain:
    def test_train_returns_metrics(self, api_url, client):
        if client:
            r = client.post("/api/train", json={"model_type": "random_forest", "n_samples": 100, "n_features": 5, "noise": 0.1})
        else:
            r = requests.post(
                f"{api_url}/api/train",
                json={"model_type": "random_forest", "n_samples": 100, "n_features": 5, "noise": 0.1},
                timeout=30,
            )
        if r.status_code == 401:
            pytest.skip("Vercel 部署保护已启用")
        assert r.status_code == 200
        data = r.json()
        assert "metrics" in data
        assert "MAE" in data["metrics"]
        assert "MAPE" in data["metrics"]
        assert "R2" in data["metrics"]
        assert data["model"] == "random_forest"


class TestPredict:
    def test_predict_returns_list(self, api_url, client):
        if client:
            r = client.post("/api/predict", json={"features": [[1.0, 2.0, -1.0, 0.5, 0.0], [0.0, 1.0, 0.0, 0.0, 1.0]]})
        else:
            r = requests.post(
                f"{api_url}/api/predict",
                json={"features": [[1.0, 2.0, -1.0, 0.5, 0.0], [0.0, 1.0, 0.0, 0.0, 1.0]]},
                timeout=30,
            )
        if r.status_code == 401:
            pytest.skip("Vercel 部署保护已启用")
        assert r.status_code == 200
        data = r.json()
        assert "predictions" in data
        assert len(data["predictions"]) == 2
