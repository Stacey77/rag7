"""
Prometheus metrics for the RAG service.

This module provides metrics collection for monitoring RAG operations,
embedding generation, search performance, and resource utilization.
"""

import time
from functools import wraps
from typing import Callable, Any, Optional

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

# RAG-specific metrics
RAG_EMBEDDINGS = Counter(
    'rag_embeddings_total',
    'Total number of embeddings generated',
    ['type']  # text, image
)

RAG_SEARCHES = Counter(
    'rag_searches_total',
    'Total number of search queries',
    ['type']  # vector, hybrid
)

RAG_QUERIES = Counter(
    'rag_queries_total',
    'Total number of RAG queries',
    ['status']  # success, error
)

RAG_OPERATION_DURATION = Histogram(
    'rag_operation_duration_seconds',
    'RAG operation duration in seconds',
    ['operation'],  # embed, search, query, rerank
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

RAG_COLLECTION_SIZE = Gauge(
    'rag_collection_size',
    'Number of documents in collection',
    ['collection']
)

MILVUS_CONNECTION_ERRORS = Counter(
    'milvus_connection_errors_total',
    'Total Milvus connection errors'
)

EMBEDDING_BATCH_SIZE = Histogram(
    'rag_embedding_batch_size',
    'Size of embedding batches',
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000]
)

SEARCH_TOP_K = Histogram(
    'rag_search_top_k',
    'Top-K parameter used in searches',
    buckets=[1, 3, 5, 10, 20, 50, 100]
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


def track_embedding(embed_type: str = 'text', batch_size: int = 1) -> None:
    """Track embedding generation."""
    RAG_EMBEDDINGS.labels(type=embed_type).inc(batch_size)
    EMBEDDING_BATCH_SIZE.observe(batch_size)


def track_search(search_type: str = 'vector', top_k: int = 10) -> None:
    """Track search operation."""
    RAG_SEARCHES.labels(type=search_type).inc()
    SEARCH_TOP_K.observe(top_k)


def track_query(success: bool = True) -> None:
    """Track RAG query."""
    status = 'success' if success else 'error'
    RAG_QUERIES.labels(status=status).inc()


def track_operation_duration(operation: str):
    """Decorator to track operation duration."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                RAG_OPERATION_DURATION.labels(operation=operation).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                RAG_OPERATION_DURATION.labels(operation=operation).observe(duration)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def update_collection_size(collection: str, size: int) -> None:
    """Update collection size gauge."""
    RAG_COLLECTION_SIZE.labels(collection=collection).set(size)


def track_milvus_error() -> None:
    """Track Milvus connection error."""
    MILVUS_CONNECTION_ERRORS.inc()


async def metrics_endpoint(request: Request) -> Response:
    """Endpoint to expose Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Import asyncio for the decorator
import asyncio
