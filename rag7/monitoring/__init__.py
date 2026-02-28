"""Monitoring and observability for the multi-LLM framework."""
from typing import Dict, Optional
from datetime import datetime
from collections import defaultdict
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry
from rag7.models import LLMProvider, ProviderMetrics


class MetricsCollector:
    """Collects and tracks metrics for LLM operations."""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        # Use custom registry or create a new one for testing
        self.registry = registry if registry is not None else CollectorRegistry()
        
        # Prometheus metrics
        self.request_counter = Counter(
            'llm_requests_total',
            'Total number of LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.token_counter = Counter(
            'llm_tokens_total',
            'Total number of tokens used',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.cost_counter = Counter(
            'llm_cost_total',
            'Total cost in USD',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.latency_histogram = Histogram(
            'llm_request_latency_seconds',
            'Request latency in seconds',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.active_requests = Gauge(
            'llm_active_requests',
            'Number of active requests',
            ['provider'],
            registry=self.registry
        )
        
        # Internal tracking
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize metrics for all providers."""
        for provider in LLMProvider:
            self.provider_metrics[provider.value] = ProviderMetrics(
                provider=provider
            )
    
    def record_request(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        latency_ms: float,
        success: bool = True
    ):
        """Record metrics for a request."""
        # Update Prometheus metrics
        status = 'success' if success else 'error'
        self.request_counter.labels(provider=provider, model=model, status=status).inc()
        
        if success:
            self.token_counter.labels(provider=provider, model=model).inc(tokens)
            self.cost_counter.labels(provider=provider, model=model).inc(cost)
            self.latency_histogram.labels(provider=provider, model=model).observe(latency_ms / 1000)
        
        # Update internal metrics
        if provider in self.provider_metrics:
            metrics = self.provider_metrics[provider]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
                metrics.total_tokens += tokens
                metrics.total_cost += cost
                
                # Update average latency
                total_successful = metrics.successful_requests
                current_avg = metrics.average_latency_ms
                metrics.average_latency_ms = (
                    (current_avg * (total_successful - 1) + latency_ms) / total_successful
                )
            else:
                metrics.failed_requests += 1
            
            metrics.last_request_time = datetime.now()
    
    def increment_active_requests(self, provider: str):
        """Increment active request count."""
        self.active_requests.labels(provider=provider).inc()
    
    def decrement_active_requests(self, provider: str):
        """Decrement active request count."""
        self.active_requests.labels(provider=provider).dec()
    
    def get_provider_metrics(self, provider: str) -> Optional[ProviderMetrics]:
        """Get metrics for a specific provider."""
        return self.provider_metrics.get(provider)
    
    def get_all_metrics(self) -> Dict[str, ProviderMetrics]:
        """Get metrics for all providers."""
        return self.provider_metrics.copy()
    
    def export_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format."""
        return generate_latest(self.registry)


class CostTracker:
    """Tracks and analyzes costs across providers."""
    
    def __init__(self):
        self.cost_by_provider: Dict[str, float] = defaultdict(float)
        self.cost_by_model: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.daily_costs: Dict[str, float] = defaultdict(float)
    
    def track_cost(self, provider: str, model: str, cost: float):
        """Track cost for a request."""
        self.cost_by_provider[provider] += cost
        self.cost_by_model[provider][model] += cost
        
        # Track daily cost
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_costs[today] += cost
    
    def get_total_cost(self) -> float:
        """Get total cost across all providers."""
        return sum(self.cost_by_provider.values())
    
    def get_provider_cost(self, provider: str) -> float:
        """Get total cost for a provider."""
        return self.cost_by_provider.get(provider, 0.0)
    
    def get_daily_cost(self, date: Optional[str] = None) -> float:
        """Get cost for a specific day."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.daily_costs.get(date, 0.0)
    
    def get_cost_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Get detailed cost breakdown by provider and model."""
        return {
            provider: dict(models)
            for provider, models in self.cost_by_model.items()
        }


class LatencyTracker:
    """Tracks and analyzes latency across providers."""
    
    def __init__(self):
        self.latencies: Dict[str, list] = defaultdict(list)
        self.max_history = 1000  # Keep last 1000 requests per provider
    
    def track_latency(self, provider: str, latency_ms: float):
        """Track latency for a request."""
        self.latencies[provider].append(latency_ms)
        
        # Trim history if needed
        if len(self.latencies[provider]) > self.max_history:
            self.latencies[provider] = self.latencies[provider][-self.max_history:]
    
    def get_average_latency(self, provider: str) -> float:
        """Get average latency for a provider."""
        latencies = self.latencies.get(provider, [])
        return sum(latencies) / len(latencies) if latencies else 0.0
    
    def get_percentile_latency(self, provider: str, percentile: float) -> float:
        """Get percentile latency for a provider."""
        latencies = sorted(self.latencies.get(provider, []))
        if not latencies:
            return 0.0
        
        index = int(len(latencies) * percentile / 100)
        return latencies[min(index, len(latencies) - 1)]


class MonitoringService:
    """Main monitoring service that coordinates all tracking."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.cost_tracker = CostTracker()
        self.latency_tracker = LatencyTracker()
    
    def record_request(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        latency_ms: float,
        success: bool = True
    ):
        """Record all metrics for a request."""
        self.metrics_collector.record_request(
            provider, model, tokens, cost, latency_ms, success
        )
        
        if success:
            self.cost_tracker.track_cost(provider, model, cost)
            self.latency_tracker.track_latency(provider, latency_ms)
    
    def get_summary(self) -> dict:
        """Get a summary of all metrics."""
        return {
            "total_cost": self.cost_tracker.get_total_cost(),
            "cost_by_provider": dict(self.cost_tracker.cost_by_provider),
            "provider_metrics": {
                name: metrics.model_dump()
                for name, metrics in self.metrics_collector.get_all_metrics().items()
            },
            "average_latencies": {
                provider: self.latency_tracker.get_average_latency(provider)
                for provider in self.latency_tracker.latencies.keys()
            }
        }


# Global monitoring service instance
monitoring_service = MonitoringService()
