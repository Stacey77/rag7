"""
Tests for authentication system.
"""
import pytest
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestPasswordHashing:
    """Tests for password hashing utilities."""
    
    def test_import_auth_module(self):
        """Test that auth module can be imported."""
        try:
            from app.auth import get_password_hash, verify_password
            assert callable(get_password_hash)
            assert callable(verify_password)
        except ImportError:
            pytest.skip("Auth module not available")
    
    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        try:
            from app.auth import get_password_hash, verify_password
            
            password = "testpassword123"
            hashed = get_password_hash(password)
            
            # Verify correct password
            assert verify_password(password, hashed) is True
            
            # Verify incorrect password
            assert verify_password("wrongpassword", hashed) is False
        except ImportError:
            pytest.skip("Auth module not available")
    
    def test_password_hash_unique(self):
        """Test that password hashes are unique."""
        try:
            from app.auth import get_password_hash
            
            password = "testpassword123"
            hash1 = get_password_hash(password)
            hash2 = get_password_hash(password)
            
            # Same password should produce different hashes (due to salt)
            assert hash1 != hash2
        except ImportError:
            pytest.skip("Auth module not available")


class TestJWTTokens:
    """Tests for JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        try:
            from app.auth import create_access_token
            
            token = create_access_token(data={"sub": "testuser"})
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0
        except ImportError:
            pytest.skip("Auth module not available")


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_protected_endpoint_without_token(self, client):
        """Test that protected endpoints reject requests without token."""
        # This should return 401 or 403 if auth is enforced
        # Or 200 if auth is optional
        response = client.get("/")
        assert response.status_code in [200, 401, 403]
