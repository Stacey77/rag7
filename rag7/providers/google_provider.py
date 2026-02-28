"""Google AI provider implementation."""
import time
from typing import Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from rag7.providers.base import BaseLLMProvider
from rag7.models import LLMRequest, LLMResponse, LLMProvider


class GoogleProvider(BaseLLMProvider):
    """Google/Gemini provider implementation."""
    
    def _initialize_client(self):
        """Initialize Google AI client."""
        genai.configure(api_key=self.api_key)
        self.default_model = self.config.get("default_model", "gemini-pro")
        self.cost_per_1k = self.config.get("cost_per_1k_tokens", {
            "gemini-pro": 0.001
        })
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost based on tokens and model."""
        cost_per_1k = self.cost_per_1k.get(model, 0.001)
        return (tokens / 1000) * cost_per_1k
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Google AI API."""
        start_time = time.time()
        
        model_name = request.model or self.default_model
        model = genai.GenerativeModel(model_name)
        
        generation_config = genai.GenerationConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens or self.config.get("max_tokens", 1000)
        )
        
        try:
            # Build prompt with system prompt if provided
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
            
            response = await model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            content = response.text
            # Approximate token count (Gemini doesn't always provide exact counts)
            tokens_used = model.count_tokens(full_prompt).total_tokens + \
                         model.count_tokens(content).total_tokens
            cost = self.calculate_cost(tokens_used, model_name)
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.GOOGLE,
                model=model_name,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "safety_ratings": [
                        {"category": r.category.name, "probability": r.probability.name}
                        for r in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )
        except Exception as e:
            raise Exception(f"Google AI API error: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check Google AI API health."""
        try:
            model = genai.GenerativeModel(self.default_model)
            await model.generate_content_async("test")
            return True
        except Exception:
            return False
