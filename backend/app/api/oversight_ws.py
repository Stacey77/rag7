"""WebSocket endpoint for real-time oversight dashboard."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.websockets import WebSocketState

from app.api.auth import validate_token, Role, ROLE_HIERARCHY


router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections with authentication and RBAC."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_roles: dict[str, list[str]] = {}
        self.subscriptions: dict[str, Set[str]] = {}  # user_id -> set of channels
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        roles: list[str]
    ):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_roles[user_id] = roles
        self.subscriptions[user_id] = {"events", "decisions"}  # Default subscriptions
    
    def disconnect(self, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_roles:
            del self.user_roles[user_id]
        if user_id in self.subscriptions:
            del self.subscriptions[user_id]
    
    def has_permission(self, user_id: str, required_roles: list[str]) -> bool:
        """Check if user has required roles."""
        user_roles = self.user_roles.get(user_id, [])
        user_permissions = set()
        for role in user_roles:
            user_permissions.update(ROLE_HIERARCHY.get(role, [role]))
        
        return any(role in user_permissions for role in required_roles)
    
    async def send_personal(self, user_id: str, message: dict):
        """Send message to a specific user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_json(message)
                except Exception:
                    self.disconnect(user_id)
    
    async def broadcast(
        self,
        message: dict,
        channel: str = "events",
        required_roles: Optional[list[str]] = None
    ):
        """Broadcast message to all subscribed users with proper roles."""
        disconnected = []
        
        for user_id, websocket in self.active_connections.items():
            # Check channel subscription
            if channel not in self.subscriptions.get(user_id, set()):
                continue
            
            # Check role requirements
            if required_roles and not self.has_permission(user_id, required_roles):
                continue
            
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({
                        "channel": channel,
                        "data": message,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            except Exception:
                disconnected.append(user_id)
        
        # Clean up disconnected clients
        for user_id in disconnected:
            self.disconnect(user_id)
    
    async def broadcast_event(self, event: dict):
        """Broadcast a decision/state event to all authenticated users."""
        await self.broadcast(event, channel="events")
    
    async def broadcast_escalation(self, escalation: dict):
        """Broadcast escalation to reviewers and admins only."""
        await self.broadcast(
            escalation,
            channel="escalations",
            required_roles=[Role.REVIEWER, Role.ADMIN]
        )
    
    def subscribe(self, user_id: str, channel: str):
        """Subscribe user to a channel."""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].add(channel)
    
    def unsubscribe(self, user_id: str, channel: str):
        """Unsubscribe user from a channel."""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].discard(channel)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_oversight(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time oversight streaming.
    
    Authentication is done via query parameter token.
    Messages are filtered based on user roles.
    
    Message types:
    - subscribe: Subscribe to a channel
    - unsubscribe: Unsubscribe from a channel
    - action: Perform an action (override, escalate) - requires proper roles
    """
    # Authenticate
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    token_data = await validate_token(token)
    if not token_data:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    user_id = token_data.sub
    roles = token_data.roles or [Role.VIEWER]
    
    # Connect
    await manager.connect(websocket, user_id, roles)
    
    try:
        # Send initial connection success message
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "roles": roles,
            "subscriptions": list(manager.subscriptions.get(user_id, set())),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_json()
                await handle_websocket_message(websocket, user_id, data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception:
        manager.disconnect(user_id)


async def handle_websocket_message(
    websocket: WebSocket,
    user_id: str,
    data: dict
):
    """Handle incoming WebSocket messages."""
    message_type = data.get("type")
    
    if message_type == "subscribe":
        channel = data.get("channel")
        if channel:
            manager.subscribe(user_id, channel)
            await websocket.send_json({
                "type": "subscribed",
                "channel": channel
            })
    
    elif message_type == "unsubscribe":
        channel = data.get("channel")
        if channel:
            manager.unsubscribe(user_id, channel)
            await websocket.send_json({
                "type": "unsubscribed",
                "channel": channel
            })
    
    elif message_type == "action":
        action = data.get("action")
        task_id = data.get("task_id")
        
        if action == "override":
            # Check permission
            if not manager.has_permission(user_id, [Role.REVIEWER, Role.ADMIN]):
                await websocket.send_json({
                    "type": "error",
                    "message": "Insufficient permissions for override"
                })
                return
            
            # Broadcast override action
            await manager.broadcast({
                "action": "override",
                "task_id": task_id,
                "user_id": user_id,
                "data": data.get("data", {})
            }, channel="actions")
            
            await websocket.send_json({
                "type": "action_acknowledged",
                "action": "override",
                "task_id": task_id
            })
        
        elif action == "escalate":
            # Check permission
            if not manager.has_permission(
                user_id, 
                [Role.AGENT_MANAGER, Role.REVIEWER, Role.ADMIN]
            ):
                await websocket.send_json({
                    "type": "error",
                    "message": "Insufficient permissions for escalation"
                })
                return
            
            # Broadcast escalation
            await manager.broadcast_escalation({
                "action": "escalate",
                "task_id": task_id,
                "user_id": user_id,
                "reason": data.get("reason", "Manual escalation")
            })
            
            await websocket.send_json({
                "type": "action_acknowledged",
                "action": "escalate",
                "task_id": task_id
            })
    
    elif message_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })


# Helper function to broadcast events from other parts of the application
async def broadcast_decision_event(event: dict):
    """Broadcast a decision event to all connected oversight clients."""
    await manager.broadcast_event(event)


async def broadcast_task_state_change(
    task_id: str,
    old_state: str,
    new_state: str,
    metadata: Optional[dict] = None
):
    """Broadcast a task state change event."""
    await manager.broadcast_event({
        "event_type": "task_state_changed",
        "task_id": task_id,
        "old_state": old_state,
        "new_state": new_state,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
