"""
Main FastAPI application for RAG7 platform.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.logging import app_logger
from app.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    app_logger.info("Starting RAG7 AI Platform...")
    app_logger.info(f"Environment: {settings.api_env}")
    yield
    app_logger.info("Shutting down RAG7 AI Platform...")


# Create FastAPI app
app = FastAPI(
    title="RAG7 AI Platform",
    description="A platform for designing, building, and deploying LLM-powered AI products",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Add metrics endpoint if enabled
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "RAG7 AI Platform",
        "version": "0.1.0",
        "status": "operational",
        "description": "Enterprise AI platform for LLM-powered products"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.api_env
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_env == "development"
    )
