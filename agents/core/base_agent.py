"""
Base Agent Class for Multi-Agent Infrastructure Platform
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


class Message:
    """Message class for inter-agent communication"""
    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.correlation_id = correlation_id or f"{sender}-{datetime.utcnow().timestamp()}"
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Base class for all agents in the platform"""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self._running = False
        
    @abstractmethod
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming message and optionally return response"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent"""
        pass
    
    async def start(self):
        """Start the agent"""
        self.logger.info(f"Starting agent {self.agent_id}")
        self._running = True
        
        if not await self.initialize():
            self.logger.error(f"Failed to initialize agent {self.agent_id}")
            self.status = AgentStatus.ERROR
            return
        
        self.status = AgentStatus.IDLE
        await self._run_loop()
    
    async def stop(self):
        """Stop the agent"""
        self.logger.info(f"Stopping agent {self.agent_id}")
        self._running = False
        self.status = AgentStatus.STOPPED
    
    async def _run_loop(self):
        """Main agent loop"""
        while self._running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                self.status = AgentStatus.PROCESSING
                self.logger.info(
                    f"Processing message from {message.sender}: {message.message_type}"
                )
                
                # Process the message
                response = await self.process_message(message)
                
                # Send response if available
                if response:
                    await self.send_message(response)
                
                self.status = AgentStatus.IDLE
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
                self.status = AgentStatus.ERROR
                await asyncio.sleep(1)
                self.status = AgentStatus.IDLE
    
    async def send_message(self, message: Message):
        """Send message to another agent via orchestrator"""
        from .agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator.get_instance()
        await orchestrator.route_message(message)
    
    async def receive_message(self, message: Message):
        """Receive message from orchestrator"""
        await self.message_queue.put(message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "queue_size": self.message_queue.qsize()
        }
