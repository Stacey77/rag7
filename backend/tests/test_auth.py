"""
Tests for JWT authentication utilities.
"""
import pytest
from datetime import timedelta, datetime, timezone
from jose import jwt

from src.utils.auth import (
    create_access_token,
    decode_access_token,
    TokenData,
    User,
    AuthException,
    JWT_SECRET,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


def test_create_access_token():
    """Test creating a JWT access token."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify the token
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    """Test creating a token with custom expiration time."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=60)
    token = create_access_token(data, expires_delta=expires_delta)
    
    # Decode and verify expiration
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    exp_timestamp = payload["exp"]
    exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    # Check that expiration is approximately 60 minutes from now
    time_diff = exp_time - datetime.now(timezone.utc)
    assert 59 <= time_diff.total_seconds() / 60 <= 61


def test_decode_access_token():
    """Test decoding a valid JWT access token."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    token_data = decode_access_token(token)
    
    assert isinstance(token_data, TokenData)
    assert token_data.username == "testuser"
    assert token_data.exp is not None


def test_decode_invalid_token():
    """Test decoding an invalid token raises AuthException."""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(AuthException) as exc_info:
        decode_access_token(invalid_token)
    
    assert "Could not validate credentials" in str(exc_info.value.message)


def test_decode_token_missing_subject():
    """Test decoding a token without 'sub' claim raises AuthException."""
    # Create token without 'sub' claim
    data = {"other": "data"}
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    with pytest.raises(AuthException) as exc_info:
        decode_access_token(token)
    
    assert "Could not validate credentials" in str(exc_info.value.message)


def test_user_model():
    """Test User model validation."""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        disabled=False
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.disabled is False


def test_token_data_model():
    """Test TokenData model validation."""
    token_data = TokenData(
        username="testuser",
        exp=datetime.now(timezone.utc)
    )
    
    assert token_data.username == "testuser"
    assert token_data.exp is not None


def test_auth_exception():
    """Test AuthException custom exception."""
    exception = AuthException("Test error", status_code=403)
    
    assert exception.message == "Test error"
    assert exception.status_code == 403
    assert str(exception) == "Test error"
