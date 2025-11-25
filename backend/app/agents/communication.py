"""Agent Communication System with ack flow, timeouts, and retries."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
import redis.asyncio as redis

from app.core import get_settings


settings = get_settings()


class TaskState(str, Enum):
    """Task state machine states."""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    ACKED = "acked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"
    ESCALATED = "escalated"


class AgentMessage:
    """Message structure for agent communication."""
    
    def __init__(
        self,
        message_id: str,
        task_id: str,
        message_type: str,
        payload: dict,
        sender_id: str,
        recipient_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.message_id = message_id
        self.task_id = task_id
        self.message_type = message_type
        self.payload = payload
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.correlation_id = correlation_id or message_id
        self.timestamp = timestamp or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "task_id": self.task_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AgentMessage":
        return cls(
            message_id=data["message_id"],
            task_id=data["task_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            sender_id=data["sender_id"],
            recipient_id=data.get("recipient_id"),
            correlation_id=data.get("correlation_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )


class AgentCommunicationSystem:
    """
    Agent communication system with ack protocol over Redis pub/sub.
    
    Features:
    - Publish tasks with configurable timeout
    - Wait for acknowledgement with retry logic
    - Exponential backoff for retries
    - Escalation after threshold failures
    """
    
    TASK_CHANNEL = "agentic:tasks"
    ACK_CHANNEL = "agentic:acks"
    ESCALATION_CHANNEL = "agentic:escalations"
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pending_acks: dict[str, asyncio.Event] = {}
        self.ack_results: dict[str, dict] = {}
        self._subscriber_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the ack listener."""
        self._subscriber_task = asyncio.create_task(self._ack_listener())
    
    async def stop(self):
        """Stop the ack listener."""
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
    
    async def _ack_listener(self):
        """Listen for acknowledgements on the ack channel."""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.ACK_CHANNEL)
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    correlation_id = data.get("correlation_id")
                    
                    if correlation_id and correlation_id in self.pending_acks:
                        self.ack_results[correlation_id] = data
                        self.pending_acks[correlation_id].set()
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe(self.ACK_CHANNEL)
            await pubsub.close()
    
    async def publish_task(
        self,
        task_id: str,
        payload: dict,
        sender_id: str = "orchestrator",
        recipient_id: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        on_state_change: Optional[Callable[[str, TaskState], Any]] = None
    ) -> tuple[bool, Optional[dict], int]:
        """
        Publish a task and wait for acknowledgement.
        
        Returns:
            Tuple of (success, ack_data, retry_count)
        """
        timeout = timeout or settings.TASK_ACK_TIMEOUT_SECONDS
        max_retries = max_retries or settings.TASK_MAX_RETRIES
        
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            task_id=task_id,
            message_type="task_assignment",
            payload=payload,
            sender_id=sender_id,
            recipient_id=recipient_id
        )
        
        retry_count = 0
        
        while retry_count <= max_retries:
            # Update state
            if on_state_change:
                state = TaskState.QUEUED if retry_count == 0 else TaskState.ASSIGNED
                await on_state_change(task_id, state)
            
            # Create ack event
            correlation_id = message.correlation_id
            self.pending_acks[correlation_id] = asyncio.Event()
            
            # Publish task
            await self.redis.publish(self.TASK_CHANNEL, json.dumps(message.to_dict()))
            
            if on_state_change:
                await on_state_change(task_id, TaskState.ASSIGNED)
            
            # Wait for ack with timeout
            try:
                backoff = settings.TASK_BACKOFF_BASE ** retry_count
                actual_timeout = timeout * backoff
                
                await asyncio.wait_for(
                    self.pending_acks[correlation_id].wait(),
                    timeout=actual_timeout
                )
                
                # Ack received
                ack_data = self.ack_results.pop(correlation_id, None)
                del self.pending_acks[correlation_id]
                
                if on_state_change:
                    await on_state_change(task_id, TaskState.ACKED)
                
                return True, ack_data, retry_count
            
            except asyncio.TimeoutError:
                # Timeout - retry with backoff
                del self.pending_acks[correlation_id]
                retry_count += 1
                
                if retry_count <= max_retries:
                    # Generate new correlation ID for retry
                    message.correlation_id = str(uuid.uuid4())
        
        # All retries exhausted - escalate
        if on_state_change:
            await on_state_change(task_id, TaskState.ESCALATED)
        
        await self._escalate_task(task_id, message, retry_count)
        
        return False, None, retry_count
    
    async def send_ack(
        self,
        correlation_id: str,
        task_id: str,
        agent_id: str,
        status: str = "acked",
        metadata: Optional[dict] = None
    ):
        """Send acknowledgement for a task."""
        ack_message = {
            "correlation_id": correlation_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "status": status,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.redis.publish(self.ACK_CHANNEL, json.dumps(ack_message))
    
    async def _escalate_task(
        self,
        task_id: str,
        original_message: AgentMessage,
        retry_count: int
    ):
        """Escalate task to human review queue."""
        escalation_message = {
            "task_id": task_id,
            "original_message": original_message.to_dict(),
            "retry_count": retry_count,
            "escalation_reason": "max_retries_exceeded",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish to escalation channel
        await self.redis.publish(
            self.ESCALATION_CHANNEL,
            json.dumps(escalation_message)
        )
        
        # Also add to a persistent escalation queue
        await self.redis.lpush(
            "agentic:escalation_queue",
            json.dumps(escalation_message)
        )
    
    async def subscribe_to_tasks(
        self,
        handler: Callable[[AgentMessage], Any]
    ) -> asyncio.Task:
        """Subscribe to task channel and handle incoming tasks."""
        async def _listener():
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(self.TASK_CHANNEL)
            
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        agent_message = AgentMessage.from_dict(data)
                        await handler(agent_message)
            except asyncio.CancelledError:
                pass
            finally:
                await pubsub.unsubscribe(self.TASK_CHANNEL)
                await pubsub.close()
        
        return asyncio.create_task(_listener())
    
    async def get_escalated_tasks(self, count: int = 10) -> list[dict]:
        """Get escalated tasks from the queue."""
        tasks = []
        for _ in range(count):
            task = await self.redis.rpop("agentic:escalation_queue")
            if task:
                tasks.append(json.loads(task))
            else:
                break
        return tasks
