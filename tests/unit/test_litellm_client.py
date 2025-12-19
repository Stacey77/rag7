"""Unit tests for LiteLLM client."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.llm.litellm_client import LiteLLMClient, CircuitBreaker


@pytest.mark.unit
def test_circuit_breaker_initialization():
    """Test circuit breaker initializes correctly."""
    cb = CircuitBreaker(failure_threshold=5, timeout=60, recovery_timeout=30)
    
    assert cb.failure_threshold == 5
    assert cb.timeout == 60
    assert cb.recovery_timeout == 30
    assert cb.failures == 0
    assert cb.state == "closed"


@pytest.mark.unit
def test_circuit_breaker_opens_on_failures():
    """Test circuit breaker opens after threshold failures."""
    cb = CircuitBreaker(failure_threshold=3)
    
    # Simulate failures
    for _ in range(3):
        try:
            cb.call(lambda: 1/0)  # Causes exception
        except:
            pass
    
    assert cb.state == "open"
    assert cb.failures >= 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_litellm_client_initialization():
    """Test LiteLLM client initializes with correct config."""
    client = LiteLLMClient()
    
    assert client.circuit_breaker is not None
    assert client.cost_tracker == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_litellm_client_tracks_costs():
    """Test LiteLLM client tracks API costs correctly."""
    client = LiteLLMClient()
    
    # Mock successful response
    mock_response = {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "model": "gemini-pro"
    }
    
    with patch('src.llm.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response):
        response = await client.complete(
            model="gemini-pro",
            messages=[{"role": "user", "content": "Hello"}]
        )
    
    assert "gemini-pro" in client.cost_tracker
    assert client.cost_tracker["gemini-pro"]["calls"] == 1
    assert client.cost_tracker["gemini-pro"]["tokens"] == 30


@pytest.mark.unit
def test_circuit_breaker_thread_safety():
    """Test circuit breaker is thread-safe."""
    import threading
    cb = CircuitBreaker(failure_threshold=10)
    
    def increment_failures():
        for _ in range(5):
            try:
                cb.call(lambda: 1/0)
            except:
                pass
    
    threads = [threading.Thread(target=increment_failures) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Should have accumulated failures thread-safely
    assert cb.failures >= 10
    assert cb.state == "open"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_litellm_client_retry_logic():
    """Test LiteLLM client retries on failures."""
    client = LiteLLMClient()
    
    call_count = 0
    
    async def failing_completion(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("API Error")
        return {
            "choices": [{"message": {"content": "Success"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            "model": "gemini-pro"
        }
    
    with patch('src.llm.litellm_client.acompletion', new_callable=AsyncMock, side_effect=failing_completion):
        response = await client.complete(
            model="gemini-pro",
            messages=[{"role": "user", "content": "Test"}]
        )
    
    # Should have retried and eventually succeeded
    assert call_count == 3
    assert response["choices"][0]["message"]["content"] == "Success"
