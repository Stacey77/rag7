"""
FastAPI Web API for RAG7 with JWT authentication.

This module provides the main API endpoints including:
- Health check (public)
- Authentication endpoints (login)
- Protected chat endpoints (require JWT)
- WebSocket chat endpoint (require JWT)

TODO: Add actual RAG functionality (vector store, LLM integration, etc.)
This is a minimal secure scaffold that can be extended.
"""

import os
from typing import Optional, Dict, Any
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.utils.auth import (
    User,
    Token,
    LoginRequest,
    authenticate_user,
    create_access_token,
    get_current_user,
    decode_access_token,
    InvalidTokenException,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


# Initialize FastAPI app
app = FastAPI(
    title="RAG7 API",
    description="RAG (Retrieval Augmented Generation) API with JWT authentication",
    version="0.1.0",
)

# CORS middleware - configure appropriately for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


class ChatRequest(BaseModel):
    """Chat request body."""
    message: str = Field(..., min_length=1, description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")


class ChatResponse(BaseModel):
    """Chat response body."""
    message: str
    user: str


# Public endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - health check.
    
    This endpoint is public and does not require authentication.
    """
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    This endpoint is public and does not require authentication.
    Used by monitoring systems and load balancers.
    """
    return HealthResponse(status="healthy", version="0.1.0")


# Authentication endpoints
@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """
    Login endpoint - authenticate and receive JWT access token.
    
    TODO: Replace static user authentication with OAuth/OIDC flow:
    1. Redirect to identity provider
    2. Handle callback with authorization code
    3. Exchange code for tokens
    4. Validate tokens and create session
    
    For MVP, this uses static username/password configured via environment.
    
    Args:
        login_request: Username and password
        
    Returns:
        Token: JWT access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = authenticate_user(login_request.username, login_request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.post("/auth/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh token endpoint - exchange current token for new token.
    
    TODO: Implement proper refresh token flow with:
    1. Separate refresh tokens (longer lived, stored securely)
    2. Refresh token rotation
    3. Revocation list for compromised tokens
    
    For MVP, this simply issues a new access token if current one is valid.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Token: New JWT access token
    """
    # Create new access token
    access_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token, token_type="bearer")


# Protected endpoints - require authentication
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chat endpoint - send a message and receive a response.
    
    This endpoint requires JWT authentication.
    
    TODO: Integrate actual RAG functionality:
    1. Retrieve relevant documents from vector store
    2. Construct prompt with context
    3. Call LLM API
    4. Return generated response
    
    Args:
        request: Chat request with message and optional context
        current_user: Authenticated user
        
    Returns:
        ChatResponse: Response message and user info
    """
    # TODO: Implement RAG logic here
    # For now, just echo back with a placeholder response
    response_message = f"Echo: {request.message} (RAG functionality to be implemented)"
    
    return ChatResponse(
        message=response_message,
        user=current_user.username
    )


@app.get("/protected/info")
async def protected_info(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint example - requires authentication.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: User information
    """
    return {
        "message": "This is a protected endpoint",
        "user": current_user.username,
        "authenticated": True
    }


# WebSocket endpoint - protected with JWT
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    
    This endpoint requires JWT authentication via query parameter or first message.
    
    TODO: Implement proper WebSocket authentication:
    1. Accept token in connection request (query param or header)
    2. Validate token before accepting connection
    3. Handle token expiration during connection
    
    For MVP, expects token in first message after connection.
    
    Authentication flow:
    1. Client connects
    2. Server accepts connection
    3. Client sends: {"type": "auth", "token": "<jwt>"}
    4. Server validates and responds
    5. Subsequent messages are processed if authenticated
    """
    await websocket.accept()
    
    authenticated = False
    current_user = None
    
    try:
        # First message should be authentication
        auth_message = await websocket.receive_json()
        
        if auth_message.get("type") == "auth":
            token = auth_message.get("token")
            if not token:
                await websocket.send_json({
                    "type": "error",
                    "message": "No token provided"
                })
                await websocket.close()
                return
            
            try:
                payload = decode_access_token(token)
                username = payload.get("sub")
                if username:
                    current_user = User(username=username)
                    authenticated = True
                    await websocket.send_json({
                        "type": "auth_success",
                        "message": f"Authenticated as {username}"
                    })
            except InvalidTokenException:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid token"
                })
                await websocket.close()
                return
        else:
            await websocket.send_json({
                "type": "error",
                "message": "First message must be authentication"
            })
            await websocket.close()
            return
        
        # Handle chat messages
        while authenticated:
            message = await websocket.receive_json()
            
            if message.get("type") == "chat":
                user_message = message.get("message", "")
                # TODO: Implement RAG logic here
                response = f"Echo: {user_message} (RAG functionality to be implemented)"
                
                await websocket.send_json({
                    "type": "chat_response",
                    "message": response,
                    "user": current_user.username
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Unknown message type"
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


# Dashboard routes (if needed in the future)
# TODO: Add dashboard endpoints with authentication
# Example:
# @app.get("/dashboard")
# async def dashboard(current_user: User = Depends(get_current_user)):
#     return {"message": "Dashboard", "user": current_user.username}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
