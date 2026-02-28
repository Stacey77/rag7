"""
LLM Service for multi-provider LLM interactions.
"""
from typing import Optional, List, Dict, Any
import asyncio

from app.core.config import settings
from app.core.logging import app_logger


class LLMService:
    """
    Service for interacting with multiple LLM providers.
    
    Supports OpenAI, Anthropic, and other providers through a unified interface.
    """
    
    def __init__(self):
        """Initialize LLM service with configured providers."""
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM provider clients."""
        try:
            if settings.openai_api_key:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                app_logger.info("OpenAI client initialized")
            
            if settings.anthropic_api_key:
                from anthropic import AsyncAnthropic
                self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
                app_logger.info("Anthropic client initialized")
        
        except Exception as e:
            app_logger.warning(f"Error initializing LLM clients: {str(e)}")
    
    async def generate_completion(
        self,
        prompt: str,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion using the specified provider.
        
        Args:
            prompt: The input prompt
            provider: LLM provider (openai, anthropic)
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_message: Optional system message
        
        Returns:
            Dictionary with completion result
        """
        if provider == "openai":
            return await self._openai_completion(
                prompt, model, temperature, max_tokens, system_message
            )
        elif provider == "anthropic":
            return await self._anthropic_completion(
                prompt, model, temperature, max_tokens, system_message
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using the specified provider.
        
        Args:
            messages: List of chat messages
            provider: LLM provider
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dictionary with completion result
        """
        if provider == "openai":
            return await self._openai_chat(messages, model, temperature, max_tokens)
        elif provider == "anthropic":
            return await self._anthropic_chat(messages, model, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _openai_completion(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
        system_message: Optional[str]
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")
        
        model = model or "gpt-3.5-turbo"
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.choices[0].message.content,
            "provider": "openai",
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Generate chat completion using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")
        
        model = model or "gpt-3.5-turbo"
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.choices[0].message.content,
            "provider": "openai",
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def _anthropic_completion(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
        system_message: Optional[str]
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Check API key.")
        
        model = model or "claude-3-sonnet-20240229"
        max_tokens = max_tokens or 1024
        
        response = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message or "",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "content": response.content[0].text,
            "provider": "anthropic",
            "model": model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    async def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Generate chat completion using Anthropic."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Check API key.")
        
        model = model or "claude-3-sonnet-20240229"
        max_tokens = max_tokens or 1024
        
        # Extract system message if present
        system_message = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        response = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=filtered_messages
        )
        
        return {
            "content": response.content[0].text,
            "provider": "anthropic",
            "model": model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
