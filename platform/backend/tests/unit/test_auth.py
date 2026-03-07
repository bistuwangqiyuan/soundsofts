"""Basic auth tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    """Test health check returns 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials() -> None:
    """Test login with invalid credentials returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "wrong"},
        )
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_missing_fields() -> None:
    """Test login with missing fields returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/login",
            json={"username": "test"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_me_unauthorized() -> None:
    """Test /me without token returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_validation() -> None:
    """Test register with invalid email returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "username": "ab",
                "email": "invalid-email",
                "password": "short",
                "role": "viewer",
            },
        )
    assert response.status_code == 422
