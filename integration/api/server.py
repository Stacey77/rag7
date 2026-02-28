"""FastAPI server exposing LangGraph capabilities."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from integration.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("Starting LangGraph API server...")
    yield
    # Shutdown
    print("Shutting down LangGraph API server...")


app = FastAPI(
    title="LangGraph Multi-Agent API",
    description="API for orchestrating multi-agent workflows using LangGraph patterns",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "langgraph-api"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LangGraph Multi-Agent API",
        "version": "0.1.0",
        "documentation": "/docs",
        "patterns": [
            "sequential",
            "parallel",
            "loop",
            "router",
            "aggregator",
            "hierarchical",
            "network",
        ],
    }


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server.

    Args:
        host: Host to bind to.
        port: Port to listen on.
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    host = os.getenv("LANGGRAPH_API_HOST", "0.0.0.0")
    port = int(os.getenv("LANGGRAPH_API_PORT", "8000"))
    run_server(host, port)
