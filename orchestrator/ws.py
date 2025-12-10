"""
WebSocket support for FortFail Orchestrator

Provides real-time event streaming to connected clients.
Supports optional JWT authentication via query parameter.
"""

import os
import json
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import jwt

# Configuration
ORCH_JWT_SECRET = os.getenv("ORCH_JWT_SECRET", "dev-jwt-secret-change-in-production")

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal(self, message: Any, websocket: WebSocket):
        """Send message to a specific WebSocket"""
        try:
            if isinstance(message, dict):
                await websocket.send_json(message)
            else:
                await websocket.send_text(str(message))
        except Exception as e:
            print(f"Error sending to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Any):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                if isinstance(message, dict):
                    await connection.send_json(message)
                else:
                    await connection.send_text(str(message))
            except Exception as e:
                print(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager instance
ws_manager = ConnectionManager()


def verify_ws_token(token: str) -> Dict[str, Any]:
    """Verify JWT token for WebSocket connection"""
    try:
        payload = jwt.decode(token, ORCH_JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time event streaming
    
    Optional authentication via query parameter: /ws?token=<jwt_token>
    """
    
    # Optional token validation
    if token:
        try:
            verify_ws_token(token)
        except ValueError as e:
            await websocket.close(code=1008, reason=str(e))
            return
    
    # Accept connection
    await ws_manager.connect(websocket)
    
    # Send welcome message
    await ws_manager.send_personal({
        "event": "connected",
        "message": "Connected to FortFail Orchestrator WebSocket"
    }, websocket)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now (could handle client commands in future)
            await ws_manager.send_personal({
                "event": "echo",
                "data": data
            }, websocket)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
