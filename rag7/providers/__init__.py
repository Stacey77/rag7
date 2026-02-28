"""Provider factory and registry."""
from typing import Dict, Type
from rag7.providers.base import BaseLLMProvider
from rag7.providers.openai_provider import OpenAIProvider
from rag7.providers.anthropic_provider import AnthropicProvider
from rag7.providers.google_provider import GoogleProvider
from rag7.models import LLMProvider as LLMProviderEnum


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        LLMProviderEnum.OPENAI: OpenAIProvider,
        LLMProviderEnum.ANTHROPIC: AnthropicProvider,
        LLMProviderEnum.GOOGLE: GoogleProvider,
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_type: str,
        api_key: str,
        config: dict = None
    ) -> BaseLLMProvider:
        """Create a provider instance."""
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return provider_class(api_key=api_key, config=config or {})
    
    @classmethod
    def register_provider(cls, provider_type: str, provider_class: Type[BaseLLMProvider]):
        """Register a new provider type."""
        cls._providers[provider_type] = provider_class
