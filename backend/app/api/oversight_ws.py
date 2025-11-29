"""WebSocket endpoint for real-time oversight."""
import asyncio
import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core import verify_oidc_token, Role
from app.agents.communication import CommunicationAgent

router = APIRouter(tags=["oversight"])


class ConnectionManager:
    """Manages WebSocket connections for oversight."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, roles: list):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.user_connections[websocket] = {
            "user_id": user_id,
            "roles": roles
        }
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        self.user_connections.pop(websocket, None)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection."""
        await websocket.send_text(message)
    
    async def broadcast(self, message: dict, required_role: str = None):
        """Broadcast message to all authorized connections."""
        message_text = json.dumps(message)
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                # Check role if required
                if required_role:
                    user_info = self.user_connections.get(connection, {})
                    roles = user_info.get("roles", [])
                    if required_role not in roles and Role.ADMIN not in roles:
                        continue
                
                await connection.send_text(message_text)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


async def verify_ws_token(token: str) -> dict:
    """Verify WebSocket authentication token."""
    payload = await verify_oidc_token(token)
    if not payload:
        return None
    
    return {
        "user_id": payload.get("sub", "unknown"),
        "email": payload.get("email"),
        "roles": payload.get("roles", ["viewer"])
    }


@router.websocket("/ws/oversight")
async def websocket_oversight(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time oversight events.
    Requires authentication via token query parameter.
    """
    # Verify token
    user = await verify_ws_token(token)
    
    if not user:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Connect
    await manager.connect(websocket, user["user_id"], user["roles"])
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connected",
                "user_id": user["user_id"],
                "roles": user["roles"],
                "message": "Connected to oversight stream"
            }),
            websocket
        )
        
        # Listen for events from Redis and broadcast
        communication = CommunicationAgent()
        await communication.connect()
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client message or timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Handle client messages (e.g., ping/pong)
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        websocket
                    )
            
            except asyncio.TimeoutError:
                # Send keepalive
                await manager.send_personal_message(
                    json.dumps({"type": "keepalive"}),
                    websocket
                )
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
    
    finally:
        manager.disconnect(websocket)
        await communication.disconnect()


@router.post("/broadcast")
async def broadcast_event(event: dict):
    """
    Broadcast an event to all oversight connections.
    (Internal endpoint - should be protected in production)
    """
    await manager.broadcast(event)
    return {"status": "broadcasted", "connections": len(manager.active_connections)}
