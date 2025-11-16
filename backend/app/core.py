"""Core configuration and utilities for the Agentic platform."""
import os
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx
from functools import lru_cache

# Configuration from environment
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET", "")
OIDC_JWKS_URL = os.getenv("OIDC_JWKS_URL", "")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# RBAC Roles
class Role:
    """RBAC role constants."""
    ADMIN = "admin"
    REVIEWER = "reviewer"
    AGENT_MANAGER = "agent_manager"
    VIEWER = "viewer"
    
    @classmethod
    def all_roles(cls):
        return [cls.ADMIN, cls.REVIEWER, cls.AGENT_MANAGER, cls.VIEWER]
    
    @classmethod
    def can_override(cls, role: str) -> bool:
        """Check if role can override agent decisions."""
        return role in [cls.ADMIN, cls.REVIEWER]
    
    @classmethod
    def can_escalate(cls, role: str) -> bool:
        """Check if role can escalate tasks."""
        return role in [cls.ADMIN, cls.REVIEWER, cls.AGENT_MANAGER]
    
    @classmethod
    def can_manage_agents(cls, role: str) -> bool:
        """Check if role can manage agents."""
        return role in [cls.ADMIN, cls.AGENT_MANAGER]


@lru_cache()
def get_settings():
    """Get application settings (cached)."""
    return {
        "oidc_issuer": OIDC_ISSUER,
        "oidc_client_id": OIDC_CLIENT_ID,
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT,
        "redis_db": REDIS_DB,
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_oidc_token(token: str) -> Optional[dict]:
    """Verify OIDC JWT token and return claims."""
    if not OIDC_ISSUER:
        # If OIDC is not configured, decode locally (dev mode)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    # In production, verify against OIDC provider
    try:
        # For simplicity, we'll decode without verification for now
        # In production, fetch JWKS and verify signature
        payload = jwt.decode(
            token, 
            SECRET_KEY,  # Should be public key from JWKS in production
            algorithms=["RS256", ALGORITHM],
            options={"verify_signature": False}  # TODO: Implement proper verification
        )
        return payload
    except JWTError:
        return None


class RedisConfig:
    """Redis connection configuration."""
    host: str = REDIS_HOST
    port: int = REDIS_PORT
    db: int = REDIS_DB
    
    @classmethod
    def get_url(cls) -> str:
        """Get Redis connection URL."""
        return f"redis://{cls.host}:{cls.port}/{cls.db}"


class TaskConfig:
    """Task orchestration configuration."""
    DEFAULT_ACK_TIMEOUT = 30  # seconds
    DEFAULT_TASK_TIMEOUT = 300  # seconds
    DEFAULT_MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 2  # exponential backoff base
    RETRY_BACKOFF_MAX = 300  # max backoff in seconds
    ESCALATION_THRESHOLD = 3  # failures before escalation
