"""LiteLLM client with retry logic, circuit breaker, and cost tracking."""
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from litellm import acompletion, completion
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..config import settings
from ..observability.logging import get_logger
from ..observability.metrics import (
    llm_api_calls_total,
    llm_api_duration_seconds,
    llm_cost_usd_total,
    llm_token_usage_total,
)
from ..observability.tracing import trace_llm_call

logger = get_logger(__name__)


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker for LLM API calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        recovery_timeout: int = 30,
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Timeout in seconds for API calls
            recovery_timeout: Time in seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self._lock = __import__('threading').Lock()
        self._failures = 0
        self._last_failure_time = 0
        self._state = "closed"  # closed, open, half-open

    @property
    def failures(self) -> int:
        """Get failure count thread-safely."""
        with self._lock:
            return self._failures

    @failures.setter
    def failures(self, value: int) -> None:
        """Set failure count thread-safely."""
        with self._lock:
            self._failures = value

    @property
    def state(self) -> str:
        """Get circuit breaker state thread-safely."""
        with self._lock:
            return self._state

    @state.setter
    def state(self, value: str) -> None:
        """Set circuit breaker state thread-safely."""
        with self._lock:
            self._state = value

    @property
    def last_failure_time(self) -> float:
        """Get last failure time thread-safely."""
        with self._lock:
            return self._last_failure_time

    @last_failure_time.setter
    def last_failure_time(self, value: float) -> None:
        """Set last failure time thread-safely."""
        with self._lock:
            self._last_failure_time = value

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker moving to half-open state")
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
                logger.info("Circuit breaker closed")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failures} failures")
            raise e


class LiteLLMClient:
    """Unified LLM client with retry, circuit breaker, and observability."""

    def __init__(self):
        """Initialize LiteLLM client."""
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=settings.circuit_breaker.failure_threshold,
            timeout=settings.circuit_breaker.timeout,
            recovery_timeout=settings.circuit_breaker.recovery_timeout,
        )
        self.cost_tracker: Dict[str, float] = {}

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Make a chat completion request.
        
        Args:
            model: Model name
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional arguments
            
        Returns:
            Completion response
        """
        provider = self._get_provider(model)
        start_time = time.time()

        try:
            with trace_llm_call(model, provider):
                response = await self.circuit_breaker.call(
                    acompletion,
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs,
                )

                # Track metrics
                duration = time.time() - start_time
                llm_api_duration_seconds.labels(model=model, provider=provider).observe(
                    duration
                )
                llm_api_calls_total.labels(
                    model=model, provider=provider, status="success"
                ).inc()

                # Track tokens and cost
                if hasattr(response, "usage"):
                    self._track_usage(model, provider, response.usage)

                logger.info(
                    "LLM completion successful",
                    model=model,
                    provider=provider,
                    duration=duration,
                )

                return response

        except Exception as e:
            duration = time.time() - start_time
            llm_api_calls_total.labels(
                model=model, provider=provider, status="error"
            ).inc()
            logger.error(
                "LLM completion failed",
                model=model,
                provider=provider,
                error=str(e),
                duration=duration,
            )
            raise

    async def stream_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response.
        
        Args:
            model: Model name
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
            
        Yields:
            Response chunks
        """
        response = await self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _get_provider(self, model: str) -> str:
        """Get provider from model name.
        
        Args:
            model: Model name
            
        Returns:
            Provider name
        """
        if "gpt" in model:
            return "openai"
        elif "claude" in model:
            return "anthropic"
        elif "gemini" in model:
            return "google"
        elif "mistral" in model:
            return "mistral"
        else:
            return "unknown"

    def _track_usage(self, model: str, provider: str, usage: Any) -> None:
        """Track token usage and cost.
        
        Args:
            model: Model name
            provider: Provider name
            usage: Usage object from response
        """
        if hasattr(usage, "prompt_tokens"):
            llm_token_usage_total.labels(
                model=model, provider=provider, token_type="input"
            ).inc(usage.prompt_tokens)

        if hasattr(usage, "completion_tokens"):
            llm_token_usage_total.labels(
                model=model, provider=provider, token_type="output"
            ).inc(usage.completion_tokens)

        # Calculate cost (simplified - use actual pricing)
        cost = self._calculate_cost(model, usage)
        if cost > 0:
            llm_cost_usd_total.labels(model=model, provider=provider).inc(cost)
            self.cost_tracker[model] = self.cost_tracker.get(model, 0) + cost

    def _calculate_cost(self, model: str, usage: Any) -> float:
        """Calculate cost of API call.
        
        Args:
            model: Model name
            usage: Usage object
            
        Returns:
            Cost in USD
        """
        # Simplified cost calculation - extend with actual pricing
        cost_per_1k_tokens = {
            "gpt-4-turbo": 0.01,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.001,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "gemini-pro": 0.00025,
            "mistral-large": 0.004,
        }

        base_cost = cost_per_1k_tokens.get(model, 0.001)
        total_tokens = getattr(usage, "total_tokens", 0)
        return (total_tokens / 1000) * base_cost

    def get_total_cost(self) -> Dict[str, float]:
        """Get total cost per model.
        
        Returns:
            Dictionary of model costs
        """
        return self.cost_tracker.copy()


# Global client instance
client = LiteLLMClient()
