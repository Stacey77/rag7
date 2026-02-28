"""Test authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test login endpoint."""
    response = await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Test get current user endpoint."""
    # First login
    login_response = await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    
    token = login_response.json()["access_token"]
    
    # Get user info
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "testuser"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to protected endpoint."""
    response = await client.get("/auth/me")
    
    assert response.status_code == 403
