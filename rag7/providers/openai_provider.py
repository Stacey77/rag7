"""OpenAI provider implementation."""
import time
from typing import Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from rag7.providers.base import BaseLLMProvider
from rag7.models import LLMRequest, LLMResponse, LLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI/GPT-4 provider implementation."""
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = self.config.get("default_model", "gpt-4")
        self.cost_per_1k = self.config.get("cost_per_1k_tokens", {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002
        })
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost based on tokens and model."""
        cost_per_1k = self.cost_per_1k.get(model, 0.03)
        return (tokens / 1000) * cost_per_1k
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API."""
        start_time = time.time()
        
        model = request.model or self.default_model
        
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or self.config.get("max_tokens", 1000)
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = self.calculate_cost(tokens_used, model)
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check OpenAI API health."""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
