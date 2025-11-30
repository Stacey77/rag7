"""Tests for models and validation."""
import pytest
from datetime import datetime
from rag7.models import (
    LLMRequest, LLMResponse, MultiLLMRequest, FusedResponse,
    LLMProvider, TaskComplexity, FusionStrategy, ProviderMetrics
)


def test_llm_request_creation():
    """Test LLM request creation."""
    request = LLMRequest(
        prompt="Test prompt",
        temperature=0.7,
        max_tokens=100
    )
    
    assert request.prompt == "Test prompt"
    assert request.temperature == 0.7
    assert request.max_tokens == 100
    assert request.provider is None


def test_llm_request_validation():
    """Test LLM request validation."""
    # Temperature out of range
    with pytest.raises(Exception):
        LLMRequest(prompt="Test", temperature=3.0)
    
    # Negative max_tokens
    with pytest.raises(Exception):
        LLMRequest(prompt="Test", max_tokens=-1)


def test_llm_response_creation():
    """Test LLM response creation."""
    response = LLMResponse(
        content="Test response",
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        tokens_used=100,
        cost=0.003,
        latency_ms=500.0
    )
    
    assert response.content == "Test response"
    assert response.provider == LLMProvider.OPENAI
    assert response.model == "gpt-4"
    assert response.tokens_used == 100
    assert isinstance(response.timestamp, datetime)


def test_multi_llm_request():
    """Test multi-LLM request creation."""
    request = MultiLLMRequest(
        prompt="Test prompt",
        providers=[LLMProvider.OPENAI, LLMProvider.ANTHROPIC],
        fusion_strategy=FusionStrategy.VOTING,
        parallel=True
    )
    
    assert len(request.providers) == 2
    assert request.fusion_strategy == FusionStrategy.VOTING
    assert request.parallel is True


def test_fused_response():
    """Test fused response creation."""
    responses = [
        LLMResponse(
            content="Response 1",
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            tokens_used=50,
            cost=0.0015,
            latency_ms=300.0
        ),
        LLMResponse(
            content="Response 2",
            provider=LLMProvider.ANTHROPIC,
            model="claude-3",
            tokens_used=60,
            cost=0.0018,
            latency_ms=350.0
        )
    ]
    
    fused = FusedResponse(
        final_content="Final response",
        individual_responses=responses,
        fusion_strategy=FusionStrategy.VOTING,
        total_cost=0.0033,
        total_latency_ms=650.0,
        confidence_score=0.85
    )
    
    assert fused.final_content == "Final response"
    assert len(fused.individual_responses) == 2
    assert fused.total_cost == 0.0033
    assert fused.confidence_score == 0.85


def test_provider_metrics():
    """Test provider metrics."""
    metrics = ProviderMetrics(
        provider=LLMProvider.OPENAI,
        total_requests=100,
        successful_requests=95,
        failed_requests=5,
        total_tokens=10000,
        total_cost=0.30,
        average_latency_ms=450.0
    )
    
    assert metrics.provider == LLMProvider.OPENAI
    assert metrics.total_requests == 100
    assert metrics.successful_requests == 95
    assert metrics.total_cost == 0.30


def test_enum_values():
    """Test enum values."""
    assert LLMProvider.OPENAI.value == "openai"
    assert LLMProvider.ANTHROPIC.value == "anthropic"
    assert LLMProvider.GOOGLE.value == "google"
    
    assert TaskComplexity.SIMPLE.value == "simple"
    assert TaskComplexity.MEDIUM.value == "medium"
    assert TaskComplexity.COMPLEX.value == "complex"
    
    assert FusionStrategy.VOTING.value == "voting"
    assert FusionStrategy.RANKING.value == "ranking"
    assert FusionStrategy.MERGING.value == "merging"
    assert FusionStrategy.FIRST.value == "first"
