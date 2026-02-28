"""Router and orchestrator for intelligent LLM selection."""
from typing import Optional, List
from rag7.models import (
    LLMRequest, LLMResponse, TaskComplexity, LLMProvider
)
from rag7.agents import agent_manager
from rag7.config import config_manager


class LLMRouter:
    """Intelligent router for selecting optimal LLM provider."""
    
    def __init__(self):
        self.config = config_manager.get_router_config()
        self.agent_manager = agent_manager
    
    def select_provider(
        self,
        request: LLMRequest,
        task_complexity: Optional[TaskComplexity] = None
    ) -> str:
        """Select the best provider based on request and configuration."""
        # If provider is explicitly specified, use it
        if request.provider:
            return request.provider.value
        
        # If task complexity is specified, use complexity-based routing
        if task_complexity:
            provider = self.config.task_complexity_routing.get(
                task_complexity.value,
                self.config.default_provider
            )
            if provider in self.agent_manager.get_available_agents():
                return provider
        
        # Cost optimization: select cheapest available provider
        if self.config.cost_optimization:
            return self._select_cheapest_provider()
        
        # Latency optimization: select fastest provider
        if self.config.latency_optimization:
            return self._select_fastest_provider()
        
        # Default provider
        default = self.config.default_provider
        if default in self.agent_manager.get_available_agents():
            return default
        
        # Fallback to any available provider
        available = self.agent_manager.get_available_agents()
        if available:
            return available[0]
        
        raise ValueError("No LLM providers available")
    
    def _select_cheapest_provider(self) -> str:
        """Select the cheapest available provider."""
        available = self.agent_manager.get_available_agents()
        
        # Cost priority: google < anthropic < openai (based on default models)
        priority = ["google", "anthropic", "openai"]
        for provider in priority:
            if provider in available:
                return provider
        
        return available[0] if available else "openai"
    
    def _select_fastest_provider(self) -> str:
        """Select the fastest provider (based on historical data)."""
        # In a real implementation, this would use historical latency data
        # For now, we'll use a simple heuristic
        available = self.agent_manager.get_available_agents()
        
        # Speed priority: openai < google < anthropic (heuristic)
        priority = ["openai", "google", "anthropic"]
        for provider in priority:
            if provider in available:
                return provider
        
        return available[0] if available else "openai"
    
    def get_fallback_chain(self, primary_provider: str) -> List[str]:
        """Get fallback chain for a provider."""
        if not self.config.enable_fallback:
            return [primary_provider]
        
        chain = [primary_provider]
        for provider in self.config.fallback_chain:
            if provider != primary_provider and provider in self.agent_manager.get_available_agents():
                chain.append(provider)
        
        return chain
    
    async def route_request(
        self,
        request: LLMRequest,
        task_complexity: Optional[TaskComplexity] = None
    ) -> LLMResponse:
        """Route request to appropriate provider with fallback support."""
        primary_provider = self.select_provider(request, task_complexity)
        fallback_chain = self.get_fallback_chain(primary_provider)
        
        last_error = None
        for provider in fallback_chain:
            try:
                response = await self.agent_manager.execute_request(provider, request)
                return response
            except Exception as e:
                last_error = e
                print(f"Provider {provider} failed: {str(e)}")
                continue
        
        raise Exception(f"All providers failed. Last error: {str(last_error)}")


class Orchestrator:
    """Orchestrates complex multi-LLM workflows."""
    
    def __init__(self):
        self.router = LLMRouter()
        self.agent_manager = agent_manager
    
    async def execute_single(
        self,
        request: LLMRequest,
        task_complexity: Optional[TaskComplexity] = None
    ) -> LLMResponse:
        """Execute a single LLM request with routing."""
        return await self.router.route_request(request, task_complexity)
    
    async def execute_parallel(
        self,
        request: LLMRequest,
        providers: Optional[List[str]] = None
    ) -> List[LLMResponse]:
        """Execute request on multiple providers in parallel."""
        if not providers:
            providers = self.agent_manager.get_available_agents()
        
        # Filter to only available providers
        available_providers = [
            p for p in providers
            if p in self.agent_manager.get_available_agents()
        ]
        
        if not available_providers:
            raise ValueError("No providers available for parallel execution")
        
        responses = await self.agent_manager.execute_parallel(available_providers, request)
        return responses
    
    async def execute_sequential(
        self,
        request: LLMRequest,
        providers: Optional[List[str]] = None
    ) -> List[LLMResponse]:
        """Execute request on multiple providers sequentially."""
        if not providers:
            providers = self.agent_manager.get_available_agents()
        
        responses = []
        for provider in providers:
            if provider in self.agent_manager.get_available_agents():
                try:
                    response = await self.agent_manager.execute_request(provider, request)
                    responses.append(response)
                except Exception as e:
                    print(f"Provider {provider} failed: {str(e)}")
                    continue
        
        return responses


# Global orchestrator instance
orchestrator = Orchestrator()
