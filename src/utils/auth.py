"""
JWT Authentication utilities for RAG7 API.

This module provides JWT token creation and verification, along with
FastAPI dependencies for protecting routes with authentication.

TODO: Replace static user authentication with OAuth/OIDC integration
for production deployment. Consider using:
- Azure AD / Entra ID
- Auth0
- Okta
- AWS Cognito
- Google OAuth
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import os
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field


# Configuration from environment variables
# JWT_SECRET must be set in production - use a cryptographically secure random string
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET environment variable must be set. "
        "Generate one with: openssl rand -hex 32"
    )
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# HTTP Bearer token security scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data model."""
    username: str
    exp: Optional[datetime] = None


class User(BaseModel):
    """User model for authentication."""
    username: str
    disabled: bool = False


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request body."""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class InvalidTokenException(Exception):
    """Custom exception for invalid or expired tokens."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password
        hashed_password: The bcrypt hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Bcrypt hashed password
    """
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time delta
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_access_token({"sub": "username"})
        >>> # Token expires in ACCESS_TOKEN_EXPIRE_MINUTES
        
        >>> token = create_access_token({"sub": "username"}, timedelta(hours=1))
        >>> # Token expires in 1 hour
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        InvalidTokenException: If token is invalid, expired, or malformed
        
    Example:
        >>> payload = decode_access_token(token)
        >>> username = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise InvalidTokenException(f"Invalid token: {str(e)}")


def get_static_users() -> Dict[str, str]:
    """
    Get static users from environment variable.
    
    TODO: Replace this with a real user database or identity provider.
    This is only for MVP/demo purposes.
    
    Returns:
        Dict[str, str]: Dictionary mapping username to hashed password
    """
    users = {}
    static_users_str = os.getenv("STATIC_USERS", "")
    
    if static_users_str:
        for user_entry in static_users_str.split(","):
            if ":" in user_entry:
                username, hashed_pwd = user_entry.split(":", 1)
                users[username.strip()] = hashed_pwd.strip()
    
    # Default user if none configured (for development only)
    if not users:
        # Default: admin / admin123
        users["admin"] = "$2b$12$zTUL72EpStgcbdytol3L9eloCwzGZx4sCYA4rYC2snOdQtHYoNVp."
    
    return users


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    TODO: Replace static user lookup with database query or identity provider.
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        Optional[User]: User object if authentication succeeds, None otherwise
    """
    users = get_static_users()
    
    if username not in users:
        return None
    
    hashed_password = users[username]
    if not verify_password(password, hashed_password):
        return None
    
    return User(username=username)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    This dependency extracts the JWT token from the Authorization header,
    validates it, and returns the user object.
    
    Args:
        credentials: HTTP Bearer token credentials from Authorization header
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: 401 if token is missing or invalid, 403 if user not found
        
    Example:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"message": f"Hello {user.username}"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except InvalidTokenException:
        raise credentials_exception
    
    # Verify user still exists in our static user list
    # TODO: Replace with database lookup or identity provider validation
    users = get_static_users()
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User no longer has access"
        )
    
    return User(username=username)


# Helper function to generate a hashed password (for setup/testing)
def generate_password_hash_for_setup(password: str) -> str:
    """
    Generate a bcrypt hash for a password.
    
    This is a helper function for setting up users during development.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Bcrypt hashed password
    """
    return get_password_hash(password)
