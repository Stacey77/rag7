"""Authentication API endpoints with OIDC support."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
import httpx

from app.core import get_settings


settings = get_settings()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# RBAC Role definitions
class Role:
    ADMIN = "admin"
    REVIEWER = "reviewer"
    AGENT_MANAGER = "agent_manager"
    VIEWER = "viewer"


ROLE_HIERARCHY = {
    Role.ADMIN: [Role.ADMIN, Role.REVIEWER, Role.AGENT_MANAGER, Role.VIEWER],
    Role.REVIEWER: [Role.REVIEWER, Role.VIEWER],
    Role.AGENT_MANAGER: [Role.AGENT_MANAGER, Role.VIEWER],
    Role.VIEWER: [Role.VIEWER],
}


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    sub: str
    email: Optional[str] = None
    roles: list[str] = []
    exp: Optional[datetime] = None


class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    roles: list[str] = []
    is_active: bool = True


class OIDCConfig(BaseModel):
    """OIDC discovery configuration."""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str


# Cache for OIDC configuration and JWKS
_oidc_config_cache: Optional[OIDCConfig] = None
_jwks_cache: Optional[dict] = None


async def get_oidc_config() -> Optional[OIDCConfig]:
    """Fetch OIDC configuration from issuer's well-known endpoint."""
    global _oidc_config_cache
    
    if not settings.OIDC_ISSUER:
        return None
    
    if _oidc_config_cache:
        return _oidc_config_cache
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.OIDC_ISSUER}/.well-known/openid-configuration"
            )
            response.raise_for_status()
            data = response.json()
            
            _oidc_config_cache = OIDCConfig(
                issuer=data["issuer"],
                authorization_endpoint=data["authorization_endpoint"],
                token_endpoint=data["token_endpoint"],
                userinfo_endpoint=data["userinfo_endpoint"],
                jwks_uri=data["jwks_uri"]
            )
            return _oidc_config_cache
        except Exception:
            return None


async def get_jwks() -> Optional[dict]:
    """Fetch JWKS from OIDC provider."""
    global _jwks_cache
    
    if _jwks_cache:
        return _jwks_cache
    
    oidc_config = await get_oidc_config()
    if not oidc_config:
        return None
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(oidc_config.jwks_uri)
            response.raise_for_status()
            _jwks_cache = response.json()
            return _jwks_cache
        except Exception:
            return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def validate_token(token: str) -> Optional[TokenData]:
    """Validate a JWT token (local or OIDC)."""
    try:
        # First try local validation
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        return TokenData(
            sub=payload.get("sub", ""),
            email=payload.get("email"),
            roles=payload.get("roles", []),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
        )
    except JWTError:
        pass
    
    # Try OIDC validation if configured
    if settings.OIDC_ISSUER:
        try:
            jwks = await get_jwks()
            if jwks:
                # In production, use proper JWKS validation
                # This is simplified for the scaffold
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,  # Would use JWKS in production
                    algorithms=["RS256", settings.JWT_ALGORITHM],
                    options={"verify_signature": False}  # Simplified for demo
                )
                
                return TokenData(
                    sub=payload.get("sub", ""),
                    email=payload.get("email"),
                    roles=payload.get("roles", payload.get("groups", [])),
                    exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
                )
        except Exception:
            pass
    
    return None


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    token_data = await validate_token(token)
    if not token_data:
        raise credentials_exception
    
    return User(
        id=token_data.sub,
        email=token_data.email or f"{token_data.sub}@local",
        roles=token_data.roles or [Role.VIEWER]
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(*required_roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(user: User = Depends(get_current_active_user)) -> User:
        user_permissions = set()
        for role in user.roles:
            user_permissions.update(ROLE_HIERARCHY.get(role, [role]))
        
        if not any(role in user_permissions for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_roles}"
            )
        return user
    
    return role_checker


# API Endpoints

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login endpoint.
    
    For development, accepts any username/password combination.
    In production, this would validate against a user database or OIDC.
    """
    # Development mode - accept any credentials
    # In production, validate against database or OIDC
    
    # Assign default roles based on username for testing
    roles = [Role.VIEWER]
    if form_data.username.startswith("admin"):
        roles = [Role.ADMIN]
    elif form_data.username.startswith("reviewer"):
        roles = [Role.REVIEWER]
    elif form_data.username.startswith("manager"):
        roles = [Role.AGENT_MANAGER]
    
    access_token = create_access_token(
        data={
            "sub": form_data.username,
            "email": f"{form_data.username}@local",
            "roles": roles
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile."""
    return current_user


@router.get("/oidc/config")
async def get_oidc_configuration():
    """Get OIDC configuration for frontend."""
    if not settings.OIDC_ISSUER:
        return {
            "enabled": False,
            "message": "OIDC not configured"
        }
    
    config = await get_oidc_config()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not fetch OIDC configuration"
        )
    
    return {
        "enabled": True,
        "issuer": config.issuer,
        "authorization_endpoint": config.authorization_endpoint,
        "client_id": settings.OIDC_CLIENT_ID
    }


@router.post("/oidc/callback")
async def oidc_callback(code: str, state: Optional[str] = None):
    """
    Handle OIDC callback and exchange code for tokens.
    
    This endpoint receives the authorization code from the OIDC provider
    and exchanges it for access and ID tokens.
    """
    oidc_config = await get_oidc_config()
    if not oidc_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OIDC not configured"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                oidc_config.token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.OIDC_CLIENT_ID,
                    "client_secret": settings.OIDC_CLIENT_SECRET,
                    "redirect_uri": f"{settings.API_V1_PREFIX}/auth/oidc/callback"
                }
            )
            response.raise_for_status()
            tokens = response.json()
            
            return {
                "access_token": tokens.get("access_token"),
                "id_token": tokens.get("id_token"),
                "token_type": tokens.get("token_type", "Bearer"),
                "expires_in": tokens.get("expires_in", 3600)
            }
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {str(e)}"
            )
