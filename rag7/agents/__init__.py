"""AI Agent implementations for each LLM provider."""
import asyncio
from typing import Optional
from rag7.providers import ProviderFactory
from rag7.providers.base import BaseLLMProvider
from rag7.models import LLMRequest, LLMResponse
from rag7.config import config_manager


class BaseAgent:
    """Base agent class with error handling and retry logic."""
    
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.request_count = 0
        self.error_count = 0
    
    async def execute(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Execute a request with error handling."""
        try:
            self.request_count += 1
            response = await self.provider.generate(request)
            return response
        except Exception as e:
            self.error_count += 1
            print(f"Agent error: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check agent health."""
        return await self.provider.health_check()


class GPT4Agent(BaseAgent):
    """GPT-4 specialized agent."""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        provider_config = config or config_manager.get_provider_config("openai").dict()
        provider = ProviderFactory.create_provider("openai", api_key, provider_config)
        super().__init__(provider)
        self.name = "GPT-4 Agent"


class ClaudeAgent(BaseAgent):
    """Claude specialized agent."""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        provider_config = config or config_manager.get_provider_config("anthropic").dict()
        provider = ProviderFactory.create_provider("anthropic", api_key, provider_config)
        super().__init__(provider)
        self.name = "Claude Agent"


class GeminiAgent(BaseAgent):
    """Gemini specialized agent."""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        provider_config = config or config_manager.get_provider_config("google").dict()
        provider = ProviderFactory.create_provider("google", api_key, provider_config)
        super().__init__(provider)
        self.name = "Gemini Agent"


class AgentManager:
    """Manages multiple agents and provides unified access."""
    
    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents based on configuration."""
        settings = config_manager.settings
        
        # Initialize OpenAI/GPT-4 agent
        if settings.openai_api_key:
            try:
                self.agents["openai"] = GPT4Agent(settings.openai_api_key)
            except Exception as e:
                print(f"Failed to initialize GPT-4 agent: {e}")
        
        # Initialize Anthropic/Claude agent
        if settings.anthropic_api_key:
            try:
                self.agents["anthropic"] = ClaudeAgent(settings.anthropic_api_key)
            except Exception as e:
                print(f"Failed to initialize Claude agent: {e}")
        
        # Initialize Google/Gemini agent
        if settings.google_api_key:
            try:
                self.agents["google"] = GeminiAgent(settings.google_api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini agent: {e}")
    
    def get_agent(self, provider: str) -> Optional[BaseAgent]:
        """Get an agent by provider name."""
        return self.agents.get(provider)
    
    def get_available_agents(self) -> list[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())
    
    async def execute_request(self, provider: str, request: LLMRequest) -> LLMResponse:
        """Execute a request on a specific agent."""
        agent = self.get_agent(provider)
        if not agent:
            raise ValueError(f"Agent not available: {provider}")
        return await agent.execute(request)
    
    async def execute_parallel(self, providers: list[str], request: LLMRequest) -> list[LLMResponse]:
        """Execute request on multiple agents in parallel."""
        tasks = []
        for provider in providers:
            agent = self.get_agent(provider)
            if agent:
                tasks.append(agent.execute(request))
        
        if not tasks:
            raise ValueError("No agents available for execution")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful responses
        responses = [r for r in results if isinstance(r, LLMResponse)]
        return responses
    
    async def health_check_all(self) -> dict[str, bool]:
        """Check health of all agents."""
        results = {}
        for name, agent in self.agents.items():
            try:
                results[name] = await agent.health_check()
            except Exception:
                results[name] = False
        return results


# Global agent manager instance
agent_manager = AgentManager()
