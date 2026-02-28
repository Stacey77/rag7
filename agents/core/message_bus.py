"""
Message Bus for Inter-Agent Communication
"""
import asyncio
import logging
from typing import Dict, List, Callable, Any
from collections import defaultdict
from .base_agent import Message

logger = logging.getLogger(__name__)


class MessageBus:
    """Pub/Sub message bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger("message_bus")
        self._running = False
    
    def subscribe(self, message_type: str, callback: Callable):
        """Subscribe to a message type"""
        self.subscribers[message_type].append(callback)
        self.logger.info(f"Subscribed to message type: {message_type}")
    
    def unsubscribe(self, message_type: str, callback: Callable):
        """Unsubscribe from a message type"""
        if callback in self.subscribers[message_type]:
            self.subscribers[message_type].remove(callback)
            self.logger.info(f"Unsubscribed from message type: {message_type}")
    
    async def publish(self, message: Message):
        """Publish a message to all subscribers"""
        await self.message_queue.put(message)
    
    async def start(self):
        """Start the message bus processing loop"""
        self._running = True
        self.logger.info("Message bus started")
        
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # Notify all subscribers of this message type
                if message.message_type in self.subscribers:
                    tasks = [
                        callback(message)
                        for callback in self.subscribers[message.message_type]
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
    
    async def stop(self):
        """Stop the message bus"""
        self._running = False
        self.logger.info("Message bus stopped")
