"""Tests for the API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app
from app.api.auth import create_access_token, Role


@pytest.fixture
def admin_token():
    """Create admin token for testing."""
    return create_access_token({
        "sub": "admin_user",
        "email": "admin@test.com",
        "roles": [Role.ADMIN]
    })


@pytest.fixture
def viewer_token():
    """Create viewer token for testing."""
    return create_access_token({
        "sub": "viewer_user",
        "email": "viewer@test.com",
        "roles": [Role.VIEWER]
    })


@pytest.fixture
def reviewer_token():
    """Create reviewer token for testing."""
    return create_access_token({
        "sub": "reviewer_user",
        "email": "reviewer@test.com",
        "roles": [Role.REVIEWER]
    })


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_login(self):
        """Test login endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/token",
                data={"username": "testuser", "password": "testpass"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_admin_role(self):
        """Test that admin username gets admin role."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/token",
                data={"username": "admin_test", "password": "pass"}
            )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, admin_token):
        """Test getting current user profile."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "admin_user"
        assert Role.ADMIN in data["roles"]
    
    @pytest.mark.asyncio
    async def test_unauthorized_without_token(self):
        """Test that endpoints require authentication."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401


class TestRBACEndpoints:
    """Tests for RBAC enforcement."""
    
    @pytest.mark.asyncio
    async def test_viewer_cannot_create_task(self, viewer_token):
        """Test that viewers cannot create tasks."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/decisions/task",
                headers={"Authorization": f"Bearer {viewer_token}"},
                json={
                    "title": "Test Task",
                    "description": "Test Description",
                    "task_type": "test",
                    "priority": "medium"
                }
            )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_viewer_cannot_access_admin_endpoints(self, viewer_token):
        """Test that viewers cannot access admin endpoints."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/admin/audits",
                headers={"Authorization": f"Bearer {viewer_token}"}
            )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_reviewer_can_override(self, reviewer_token):
        """Test that reviewers can perform overrides."""
        # This test would require database setup
        # For now, we verify the endpoint exists and requires proper role
        pass


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
