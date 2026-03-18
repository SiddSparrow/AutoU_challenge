import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        async with client as c:
            response = await c.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "email-classifier-api"


class TestClassifyTextEndpoint:
    @pytest.mark.asyncio
    async def test_empty_text_returns_422(self, client):
        async with client as c:
            response = await c.post("/api/classify/text", json={"text": ""})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_short_text_returns_422(self, client):
        async with client as c:
            response = await c.post("/api/classify/text", json={"text": "Hi"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_text_returns_422(self, client):
        async with client as c:
            response = await c.post("/api/classify/text", json={})
        assert response.status_code == 422


class TestClassifyFileEndpoint:
    @pytest.mark.asyncio
    async def test_unsupported_file_type_returns_415(self, client):
        async with client as c:
            response = await c.post(
                "/api/classify/file",
                files={"file": ("test.png", b"fake image", "image/png")},
            )
        assert response.status_code == 415
