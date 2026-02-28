"""Communication agent module for inter-agent and human communication."""
import asyncio
from typing import Optional, Dict, Any
import redis.asyncio as redis
import json
from datetime import datetime

from app.core import RedisConfig, TaskConfig


class CommunicationAgent:
    """Handles communication between agents, systems, and humans."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub = None
        self.subscriptions = set()
    
    async def connect(self):
        """Connect to Redis for pub/sub."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                RedisConfig.get_url(),
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
    
    async def publish_task(self, task_id: int, task_data: Dict[str, Any]) -> bool:
        """Publish a task to the task queue."""
        await self.connect()
        channel = "tasks:new"
        message = json.dumps({
            "task_id": task_id,
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.redis_client.publish(channel, message)
        return True
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Publish an event to the event stream."""
        await self.connect()
        channel = f"events:{event_type}"
        message = json.dumps({
            "event_type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.redis_client.publish(channel, message)
        return True
    
    async def wait_for_ack(
        self, 
        task_id: int, 
        timeout: int = TaskConfig.DEFAULT_ACK_TIMEOUT
    ) -> Optional[Dict[str, Any]]:
        """Wait for acknowledgement of a task."""
        await self.connect()
        ack_channel = f"ack:{task_id}"
        
        # Subscribe to ack channel
        async with self.redis_client.pubsub() as pubsub:
            await pubsub.subscribe(ack_channel)
            
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self._wait_for_message(pubsub),
                    timeout=timeout
                )
                
                if message and message.get("type") == "message":
                    data = json.loads(message.get("data", "{}"))
                    return data
                
                return None
            except asyncio.TimeoutError:
                return None
            finally:
                await pubsub.unsubscribe(ack_channel)
    
    async def _wait_for_message(self, pubsub):
        """Wait for a message from pubsub."""
        async for message in pubsub.listen():
            if message.get("type") == "message":
                return message
    
    async def send_ack(self, task_id: int, agent_id: int, accepted: bool = True) -> bool:
        """Send acknowledgement for a task."""
        await self.connect()
        ack_channel = f"ack:{task_id}"
        message = json.dumps({
            "task_id": task_id,
            "agent_id": agent_id,
            "accepted": accepted,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.redis_client.publish(ack_channel, message)
        return True
    
    async def subscribe_to_tasks(self, callback):
        """Subscribe to new tasks."""
        await self.connect()
        async with self.redis_client.pubsub() as pubsub:
            await pubsub.subscribe("tasks:new")
            self.subscriptions.add("tasks:new")
            
            async for message in pubsub.listen():
                if message.get("type") == "message":
                    data = json.loads(message.get("data", "{}"))
                    await callback(data)
    
    async def notify_oversight(self, event_type: str, data: Dict[str, Any]):
        """Notify oversight system of important events."""
        await self.connect()
        channel = "oversight:events"
        message = json.dumps({
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.redis_client.publish(channel, message)
