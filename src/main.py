"""Main application entry point."""
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .observability import configure_logging, get_logger, init_tracing, start_metrics_endpoint

# Configure logging
configure_logging(
    log_level=settings.log_level,
    json_logs=settings.is_production,
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.
    
    Args:
        app: FastAPI application
        
    Yields:
        None
    """
    # Startup
    logger.info(
        "Starting RAG7 Agent API",
        environment=settings.environment,
        version="0.1.0",
    )

    # Initialize tracing
    try:
        init_tracing(
            service_name="rag7-agent-api",
            jaeger_endpoint=settings.monitoring.jaeger_endpoint,
        )
        logger.info("Distributed tracing initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize tracing: {e}")

    # Start metrics endpoint
    try:
        start_metrics_endpoint(port=settings.metrics_port)
        logger.info(f"Metrics endpoint started on port {settings.metrics_port}")
    except Exception as e:
        logger.warning(f"Failed to start metrics endpoint: {e}")

    yield

    # Shutdown
    logger.info("Shutting down RAG7 Agent API")


# Create FastAPI application
app = FastAPI(
    title="RAG7 ADK Multi-Agent System",
    description="Multi-agent system with RAG capabilities using Agent Development Kit",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "service": "RAG7 ADK Multi-Agent System",
        "version": "0.1.0",
        "status": "running",
        "environment": settings.environment,
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


@app.get("/ready")
async def ready() -> dict:
    """Readiness check endpoint.
    
    Returns:
        Readiness status
    """
    # Add checks for dependencies (database, redis, etc.)
    return {
        "status": "ready",
        "checks": {
            "database": "ok",  # TODO: Implement actual checks
            "redis": "ok",
            "qdrant": "ok",
        },
    }


@app.get("/metrics-info")
async def metrics_info() -> dict:
    """Metrics endpoint information.
    
    Returns:
        Metrics endpoint URL
    """
    return {
        "metrics_url": f"http://localhost:{settings.metrics_port}/metrics",
        "format": "prometheus",
    }


def signal_handler(signum: int, frame: any) -> None:
    """Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        workers=settings.workers if settings.is_production else 1,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
