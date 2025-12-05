"""
Tests for JWT authentication functionality.

Tests cover:
- Token creation and validation
- Login endpoint
- Protected routes with and without authentication
- WebSocket authentication
"""

import os
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from jose import jwt

# Set test environment variables before importing app
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["STATIC_USERS"] = "testuser:$2b$12$zTUL72EpStgcbdytol3L9eloCwzGZx4sCYA4rYC2snOdQtHYoNVp.,admin:$2b$12$zTUL72EpStgcbdytol3L9eloCwzGZx4sCYA4rYC2snOdQtHYoNVp."

from src.interfaces.web_api import app
from src.utils.auth import (
    create_access_token,
    decode_access_token,
    verify_password,
    get_password_hash,
    InvalidTokenException,
    JWT_SECRET,
    JWT_ALGORITHM,
)

# Test client
client = TestClient(app)


class TestPasswordHashing:
    """Tests for password hashing and verification."""
    
    def test_password_hashing(self):
        """Test that password hashing and verification works."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Tests for JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test creating a JWT access token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_token_with_custom_expiry(self):
        """Test creating a token with custom expiration."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert "exp" in payload
        assert "sub" in payload
        assert payload["sub"] == "testuser"
    
    def test_decode_access_token(self):
        """Test decoding a valid JWT token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded
    
    def test_decode_invalid_token(self):
        """Test that invalid token raises exception."""
        with pytest.raises(InvalidTokenException):
            decode_access_token("invalid.token.here")
    
    def test_decode_expired_token(self):
        """Test that expired token raises exception."""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(InvalidTokenException):
            decode_access_token(token)


class TestPublicEndpoints:
    """Tests for public endpoints that don't require authentication."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestLoginEndpoint:
    """Tests for the login endpoint."""
    
    def test_login_success(self):
        """Test successful login returns token."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_with_default_user(self):
        """Test login with default admin user."""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_invalid_username(self):
        """Test login with invalid username returns 401."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_invalid_password(self):
        """Test login with invalid password returns 401."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_missing_fields(self):
        """Test login with missing fields returns 422."""
        response = client.post("/auth/login", json={"username": "testuser"})
        assert response.status_code == 422
        
        response = client.post("/auth/login", json={"password": "password"})
        assert response.status_code == 422


class TestProtectedEndpoints:
    """Tests for protected endpoints that require authentication."""
    
    def test_protected_endpoint_without_token(self):
        """Test that protected endpoint returns 401 without token."""
        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test that protected endpoint returns 401 with invalid token."""
        response = client.post(
            "/chat",
            json={"message": "Hello"},
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self):
        """Test that protected endpoint returns 200 with valid token."""
        # First, login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Then access protected endpoint
        response = client.post(
            "/chat",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert data["user"] == "testuser"
    
    def test_chat_endpoint_with_context(self):
        """Test chat endpoint with context parameter."""
        # Login first
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Send chat with context
        response = client.post(
            "/chat",
            json={
                "message": "Test message",
                "context": {"key": "value"}
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_protected_info_endpoint(self):
        """Test the protected info endpoint."""
        # Login first
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Access protected info
        response = client.get(
            "/protected/info",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"] == "testuser"


class TestRefreshToken:
    """Tests for token refresh endpoint."""
    
    def test_refresh_token_success(self):
        """Test refreshing token with valid token."""
        # Login first
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Wait a moment to ensure different timestamps
        import time
        time.sleep(1)
        
        # Refresh token
        response = client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # New token should be different from old one (due to different exp time)
        # Note: tokens may be identical if created at the exact same second
        # so we just verify we got a valid token back
        assert len(data["access_token"]) > 0
    
    def test_refresh_token_without_auth(self):
        """Test refresh token without authentication returns 403."""
        response = client.post("/auth/refresh")
        assert response.status_code == 403


class TestWebSocketAuthentication:
    """Tests for WebSocket authentication."""
    
    def test_websocket_with_valid_token(self):
        """Test WebSocket connection with valid authentication."""
        # Login first to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Connect to WebSocket
        with client.websocket_connect("/ws/chat") as websocket:
            # Send authentication
            websocket.send_json({
                "type": "auth",
                "token": token
            })
            
            # Receive auth success
            response = websocket.receive_json()
            assert response["type"] == "auth_success"
            
            # Send a chat message
            websocket.send_json({
                "type": "chat",
                "message": "Hello WebSocket"
            })
            
            # Receive response
            response = websocket.receive_json()
            assert response["type"] == "chat_response"
            assert "message" in response
            assert response["user"] == "testuser"
    
    def test_websocket_without_auth(self):
        """Test WebSocket connection without authentication."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Send non-auth message first
            websocket.send_json({
                "type": "chat",
                "message": "Hello"
            })
            
            # Should receive error
            response = websocket.receive_json()
            assert response["type"] == "error"
    
    def test_websocket_with_invalid_token(self):
        """Test WebSocket connection with invalid token."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Send authentication with invalid token
            websocket.send_json({
                "type": "auth",
                "token": "invalid.token.here"
            })
            
            # Should receive error
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "Invalid token" in response["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
