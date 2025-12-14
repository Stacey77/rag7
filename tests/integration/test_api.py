"""Integration tests for the API."""
import pytest
from httpx import AsyncClient
from src.main import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ready_endpoint():
    """Test readiness check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ready")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "RAG7 ADK Multi-Agent System"
    assert "version" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_info_endpoint():
    """Test metrics info endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/metrics-info")
        
    assert response.status_code == 200
    data = response.json()
    assert "metrics_url" in data
    assert data["format"] == "prometheus"
