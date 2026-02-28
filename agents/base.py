"""
Base classes for LLM agents in the RAG7 multi-LLM architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class AgentRequest:
    """Represents a request to an LLM agent."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResponse:
    """Represents a response from an LLM agent."""
    content: str
    agent_name: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    success: bool = True


class BaseLLMAgent(ABC):
    """
    Abstract base class for all LLM agents.
    
    This defines the interface that all agents (GPT-4, Claude, Gemini)
    must implement to work with the fusion layer.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            name: Unique name for this agent instance
            config: Configuration dictionary for the agent
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agents.{name}")
    
    @abstractmethod
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request and return a response.
        
        Args:
            request: The agent request to process
            
        Returns:
            AgentResponse with the result
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the agent is properly configured.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return information about agent capabilities.
        
        Returns:
            Dictionary describing agent capabilities
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "config": self.config
        }
