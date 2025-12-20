"""
FastAPI main application with JWT authentication.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import timedelta
from typing import Optional

from src.utils.auth import (
    create_access_token,
    decode_access_token,
    User,
    TokenData,
    AuthException,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="RAG7 API", version="0.1.0")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


# Mock user database (in production, use a real database)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": "fakehashedpassword",  # In production, use proper password hashing
        "disabled": False,
    }
}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    FastAPI dependency to validate JWT token and return current user.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
        
        if token_data.username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # In production, fetch user from database
        user_dict = fake_users_db.get(token_data.username)
        if user_dict is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = User(**user_dict)
        
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
        
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RAG7 API - JWT Authentication Demo"}


@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """
    Login endpoint to obtain JWT token.
    
    In production, validate credentials against a real database with proper password hashing.
    """
    # Simple credential check (in production, use proper authentication)
    user_dict = fake_users_db.get(login_request.username)
    
    if not user_dict or login_request.password != "testpassword":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_request.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint - returns current user information.
    Requires valid JWT token in Authorization header.
    """
    return current_user


@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Example protected route that requires authentication.
    """
    return {
        "message": f"Hello {current_user.username}! This is a protected route.",
        "user": current_user.model_dump()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
