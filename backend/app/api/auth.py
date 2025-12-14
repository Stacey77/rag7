"""Authentication and authorization API endpoints."""
from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import (
    verify_oidc_token, 
    create_access_token, 
    Role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.db.session import get_db
from app.db.crud import AuditCRUD

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int


class User(BaseModel):
    """User model from token claims."""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = []


class LoginRequest(BaseModel):
    """Login request (for dev/testing)."""
    username: str
    password: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current user from JWT token."""
    token = credentials.credentials
    
    # Verify token
    payload = await verify_oidc_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user info from token
    user = User(
        user_id=payload.get("sub", "unknown"),
        email=payload.get("email"),
        name=payload.get("name"),
        roles=payload.get("roles", ["viewer"])
    )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (add additional checks if needed)."""
    return current_user


def require_role(required_role: str):
    """Dependency to require a specific role."""
    async def role_checker(user: User = Depends(get_current_user)):
        if required_role not in user.roles and Role.ADMIN not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker


def require_any_role(*roles: str):
    """Dependency to require any of the specified roles."""
    async def role_checker(user: User = Depends(get_current_user)):
        user_roles = set(user.roles)
        required_roles = set(roles)
        
        if not user_roles.intersection(required_roles) and Role.ADMIN not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {roles} required"
            )
        return user
    return role_checker


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint (dev/testing only).
    In production, redirect to OIDC provider.
    """
    # This is a simplified dev login - in production use OIDC flow
    # For now, accept any username/password and generate token
    
    token_data = {
        "sub": request.username,
        "email": f"{request.username}@example.com",
        "name": request.username,
        "roles": ["admin", "reviewer", "agent_manager", "viewer"]  # Grant all roles for dev
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    # Log authentication event
    await AuditCRUD.create_audit(
        db,
        action="user_login",
        user_id=request.username,
        user_role="admin",
        details={"method": "dev_login"}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/roles")
async def get_available_roles():
    """Get list of available roles."""
    return {
        "roles": Role.all_roles(),
        "role_permissions": {
            "admin": ["all"],
            "reviewer": ["override", "escalate", "view"],
            "agent_manager": ["escalate", "manage_agents", "view"],
            "viewer": ["view"]
        }
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout endpoint."""
    # Log logout event
    await AuditCRUD.create_audit(
        db,
        action="user_logout",
        user_id=current_user.user_id,
        user_role=current_user.roles[0] if current_user.roles else "viewer"
    )
    
    return {"message": "Logged out successfully"}
