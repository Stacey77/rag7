"""
Tests for FastAPI authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from main import app, fake_users_db
from src.utils.auth import create_access_token

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_login_success():
    """Test successful login with valid credentials."""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_nonexistent_user():
    """Test login with non-existent user."""
    response = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "testpassword"}
    )
    
    assert response.status_code == 401


def test_protected_route_without_token():
    """Test accessing protected route without token."""
    response = client.get("/protected")
    
    assert response.status_code == 403


def test_protected_route_with_invalid_token():
    """Test accessing protected route with invalid token."""
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    
    assert response.status_code == 401


def test_protected_route_with_valid_token():
    """Test accessing protected route with valid token."""
    # First, login to get a token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Access protected route with token
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "testuser" in data["message"]
    assert "user" in data


def test_read_users_me():
    """Test /auth/me endpoint to get current user info."""
    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"
    assert user_data["full_name"] == "Test User"


def test_get_current_user_with_expired_token():
    """Test accessing protected route with expired token."""
    # Create an expired token
    expired_token = create_access_token(
        data={"sub": "testuser"},
        expires_delta=timedelta(minutes=-1)  # Already expired
    )
    
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    assert response.status_code == 401
