"""Tests for monitoring and metrics."""
import pytest
from prometheus_client import CollectorRegistry
from rag7.monitoring import MetricsCollector, CostTracker, LatencyTracker, MonitoringService
from rag7.models import LLMProvider


@pytest.fixture
def clean_registry():
    """Create a clean CollectorRegistry for each test."""
    return CollectorRegistry()


def test_metrics_collector_initialization(clean_registry):
    """Test metrics collector initialization."""
    collector = MetricsCollector(registry=clean_registry)
    
    assert collector.provider_metrics is not None
    assert len(collector.provider_metrics) > 0


def test_metrics_collector_record_success(clean_registry):
    """Test recording successful request."""
    collector = MetricsCollector(registry=clean_registry)
    
    collector.record_request(
        provider="openai",
        model="gpt-4",
        tokens=100,
        cost=0.003,
        latency_ms=500.0,
        success=True
    )
    
    metrics = collector.get_provider_metrics("openai")
    assert metrics.total_requests == 1
    assert metrics.successful_requests == 1
    assert metrics.failed_requests == 0
    assert metrics.total_tokens == 100
    assert metrics.total_cost == 0.003


def test_metrics_collector_record_failure(clean_registry):
    """Test recording failed request."""
    collector = MetricsCollector(registry=clean_registry)
    
    collector.record_request(
        provider="openai",
        model="gpt-4",
        tokens=0,
        cost=0.0,
        latency_ms=100.0,
        success=False
    )
    
    metrics = collector.get_provider_metrics("openai")
    assert metrics.total_requests == 1
    assert metrics.successful_requests == 0
    assert metrics.failed_requests == 1


def test_metrics_collector_average_latency(clean_registry):
    """Test average latency calculation."""
    collector = MetricsCollector(registry=clean_registry)
    
    collector.record_request("openai", "gpt-4", 100, 0.003, 500.0, True)
    collector.record_request("openai", "gpt-4", 100, 0.003, 700.0, True)
    
    metrics = collector.get_provider_metrics("openai")
    assert metrics.average_latency_ms == 600.0


def test_cost_tracker():
    """Test cost tracking."""
    tracker = CostTracker()
    
    tracker.track_cost("openai", "gpt-4", 0.003)
    tracker.track_cost("openai", "gpt-4", 0.002)
    tracker.track_cost("anthropic", "claude-3", 0.005)
    
    assert tracker.get_total_cost() == 0.010
    assert tracker.get_provider_cost("openai") == 0.005
    assert tracker.get_provider_cost("anthropic") == 0.005


def test_cost_tracker_breakdown():
    """Test cost breakdown by provider and model."""
    tracker = CostTracker()
    
    tracker.track_cost("openai", "gpt-4", 0.003)
    tracker.track_cost("openai", "gpt-3.5-turbo", 0.001)
    
    breakdown = tracker.get_cost_breakdown()
    assert "openai" in breakdown
    assert breakdown["openai"]["gpt-4"] == 0.003
    assert breakdown["openai"]["gpt-3.5-turbo"] == 0.001


def test_latency_tracker():
    """Test latency tracking."""
    tracker = LatencyTracker()
    
    tracker.track_latency("openai", 500.0)
    tracker.track_latency("openai", 700.0)
    tracker.track_latency("openai", 600.0)
    
    avg = tracker.get_average_latency("openai")
    assert avg == 600.0


def test_latency_tracker_percentile():
    """Test percentile latency calculation."""
    tracker = LatencyTracker()
    
    for latency in [100, 200, 300, 400, 500]:
        tracker.track_latency("openai", float(latency))
    
    p50 = tracker.get_percentile_latency("openai", 50)
    p95 = tracker.get_percentile_latency("openai", 95)
    
    assert p50 == 300.0
    assert p95 == 500.0


def test_monitoring_service():
    """Test monitoring service integration."""
    # Note: MonitoringService creates its own MetricsCollector with default registry
    # This test should work because it's isolated
    service = MonitoringService()
    
    service.record_request(
        provider="openai",
        model="gpt-4",
        tokens=100,
        cost=0.003,
        latency_ms=500.0,
        success=True
    )
    
    summary = service.get_summary()
    
    assert summary["total_cost"] == 0.003
    assert "openai" in summary["cost_by_provider"]
    assert "openai" in summary["provider_metrics"]
    assert "openai" in summary["average_latencies"]


def test_monitoring_service_multiple_providers():
    """Test monitoring with multiple providers."""
    service = MonitoringService()
    
    service.record_request("openai", "gpt-4", 100, 0.003, 500.0, True)
    service.record_request("anthropic", "claude-3", 120, 0.004, 600.0, True)
    
    summary = service.get_summary()
    
    assert summary["total_cost"] == 0.007
    assert len(summary["cost_by_provider"]) == 2
