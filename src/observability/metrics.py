"""Prometheus metrics for monitoring agent and LLM operations."""
from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import start_http_server as start_metrics_server

# Agent metrics
agent_task_duration_seconds = Histogram(
    "agent_task_duration_seconds",
    "Time spent processing agent tasks",
    ["agent_name", "task_type", "status"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)

agent_tasks_total = Counter(
    "agent_tasks_total",
    "Total number of agent tasks processed",
    ["agent_name", "task_type", "status"],
)

active_agents = Gauge(
    "active_agents",
    "Number of currently active agents",
    ["agent_type"],
)

# LLM API metrics
llm_api_calls_total = Counter(
    "llm_api_calls_total",
    "Total number of LLM API calls",
    ["model", "provider", "status"],
)

llm_api_duration_seconds = Histogram(
    "llm_api_duration_seconds",
    "Duration of LLM API calls",
    ["model", "provider"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

llm_token_usage_total = Counter(
    "llm_token_usage_total",
    "Total number of tokens used",
    ["model", "provider", "token_type"],
)

llm_cost_usd_total = Counter(
    "llm_cost_usd_total",
    "Total cost in USD for LLM API calls",
    ["model", "provider"],
)

llm_cache_hits_total = Counter(
    "llm_cache_hits_total",
    "Total number of LLM cache hits",
    ["model"],
)

llm_cache_misses_total = Counter(
    "llm_cache_misses_total",
    "Total number of LLM cache misses",
    ["model"],
)

# Circuit breaker metrics
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["service"],
)

circuit_breaker_failures_total = Counter(
    "circuit_breaker_failures_total",
    "Total number of circuit breaker failures",
    ["service"],
)

# System metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
)

# Queue metrics
queue_depth = Gauge(
    "queue_depth",
    "Number of items in the queue",
    ["queue_name"],
)

# Database metrics
db_connection_pool_size = Gauge(
    "db_connection_pool_size",
    "Number of database connections in the pool",
    ["pool_name"],
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Duration of database queries",
    ["operation"],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
)


def start_metrics_endpoint(port: int = 9090) -> None:
    """Start the Prometheus metrics HTTP server.
    
    Args:
        port: Port to expose metrics on (default: 9090)
    """
    start_metrics_server(port)
