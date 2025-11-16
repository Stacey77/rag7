"""Anthropic provider implementation."""
import time
from typing import Optional
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from rag7.providers.base import BaseLLMProvider
from rag7.models import LLMRequest, LLMResponse, LLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic/Claude provider implementation."""
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.default_model = self.config.get("default_model", "claude-3-opus-20240229")
        self.cost_per_1k = self.config.get("cost_per_1k_tokens", {
            "claude-3-opus-20240229": 0.015,
            "claude-3-sonnet-20240229": 0.003
        })
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost based on tokens and model."""
        cost_per_1k = self.cost_per_1k.get(model, 0.015)
        return (tokens / 1000) * cost_per_1k
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API."""
        start_time = time.time()
        
        model = request.model or self.default_model
        
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=request.max_tokens or self.config.get("max_tokens", 1000),
                temperature=request.temperature,
                system=request.system_prompt or "",
                messages=[
                    {"role": "user", "content": request.prompt}
                ]
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            content = response.content[0].text
            # Approximate token count (Claude doesn't always return exact counts)
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self.calculate_cost(tokens_used, model)
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.ANTHROPIC,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check Anthropic API health."""
        try:
            # Simple test request
            await self.client.messages.create(
                model=self.default_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
