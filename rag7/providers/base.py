"""Base provider abstraction for LLM providers."""
from abc import ABC, abstractmethod
from typing import Optional
from rag7.models import LLMRequest, LLMResponse


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        self.api_key = api_key
        self.config = config or {}
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider's client."""
        pass
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        pass
    
    @abstractmethod
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate the cost for the given number of tokens."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        pass
