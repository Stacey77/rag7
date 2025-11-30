"""
Prometheus metrics for the Ragamuffin backend.

This module provides metrics collection for monitoring API performance,
request rates, and resource utilization.
"""

import time
from functools import wraps
from typing import Callable, Any

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'handler', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'handler'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'handler']
)

FLOW_EXECUTIONS = Counter(
    'flow_executions_total',
    'Total number of flow executions',
    ['status']
)

FLOW_EXECUTION_DURATION = Histogram(
    'flow_execution_duration_seconds',
    'Flow execution duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

AUTH_ATTEMPTS = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['type', 'status']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        handler = request.url.path
        
        # Increment in-progress gauge
        REQUESTS_IN_PROGRESS.labels(method=method, handler=handler).inc()
        
        # Track request timing
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception as e:
            status = "500"
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, handler=handler, status=status).inc()
            REQUEST_LATENCY.labels(method=method, handler=handler).observe(duration)
            REQUESTS_IN_PROGRESS.labels(method=method, handler=handler).dec()
        
        return response


def track_flow_execution(func: Callable) -> Callable:
    """Decorator to track flow execution metrics."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            FLOW_EXECUTIONS.labels(status='success').inc()
            return result
        except Exception as e:
            FLOW_EXECUTIONS.labels(status='error').inc()
            raise
        finally:
            duration = time.time() - start_time
            FLOW_EXECUTION_DURATION.observe(duration)
    return wrapper


def track_auth_attempt(auth_type: str, success: bool) -> None:
    """Track authentication attempt."""
    status = 'success' if success else 'failure'
    AUTH_ATTEMPTS.labels(type=auth_type, status=status).inc()


async def metrics_endpoint(request: Request) -> Response:
    """Endpoint to expose Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
