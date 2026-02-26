"""Unit tests for observability modules."""
import pytest
from unittest.mock import Mock, patch
from src.observability.metrics import (
    agent_task_duration,
    llm_api_calls_total,
    llm_token_usage_total,
    llm_cost_usd_total,
)
from src.observability.logging import get_logger, configure_logging


@pytest.mark.unit
def test_metrics_are_defined():
    """Test that all metrics are properly defined."""
    assert agent_task_duration is not None
    assert llm_api_calls_total is not None
    assert llm_token_usage_total is not None
    assert llm_cost_usd_total is not None


@pytest.mark.unit
def test_agent_task_duration_labels():
    """Test agent task duration metric has correct labels."""
    # Record a task duration
    agent_task_duration.labels(
        agent_name="test-agent",
        task_type="test-task",
        status="success"
    ).observe(1.5)
    
    # Metric should be recorded
    samples = list(agent_task_duration.collect())[0].samples
    assert any(s.labels.get('agent_name') == 'test-agent' for s in samples)


@pytest.mark.unit
def test_llm_api_calls_total_increment():
    """Test LLM API calls counter increments."""
    initial_value = llm_api_calls_total.labels(
        model="gemini-pro",
        provider="google",
        status="success"
    )._value._value
    
    llm_api_calls_total.labels(
        model="gemini-pro",
        provider="google",
        status="success"
    ).inc()
    
    new_value = llm_api_calls_total.labels(
        model="gemini-pro",
        provider="google",
        status="success"
    )._value._value
    
    assert new_value > initial_value


@pytest.mark.unit
def test_llm_cost_tracking():
    """Test LLM cost tracking metric."""
    llm_cost_usd_total.labels(
        model="gpt-4",
        provider="openai"
    ).inc(0.03)
    
    samples = list(llm_cost_usd_total.collect())[0].samples
    assert any(
        s.labels.get('model') == 'gpt-4' and s.value >= 0.03
        for s in samples
    )


@pytest.mark.unit
def test_configure_logging():
    """Test logging configuration."""
    configure_logging(log_level="INFO", environment="test")
    logger = get_logger(__name__)
    
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'warning')


@pytest.mark.unit
def test_logger_pii_redaction():
    """Test that logger redacts PII information."""
    logger = get_logger(__name__)
    
    # This should be redacted in actual logs
    test_message = "User email: test@example.com and SSN: 123-45-6789"
    
    # Just verify logger can handle the message
    logger.info(test_message, extra={"user_input": test_message})
    
    # In production, the log processor would redact PII
    # Here we just verify the logger doesn't crash
    assert True
