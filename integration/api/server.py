"""
RAG7 Integration API Server

FastAPI-based integration layer for LangGraph orchestration.
Provides REST endpoints for graph execution, health checks, and monitoring.
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import httpx

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_API_URL", "http://langgraph:8123")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Initialize FastAPI app
app = FastAPI(
    title="RAG7 Integration API",
    description="Integration layer for LangGraph-based RAG system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request/Response Models
class GraphInput(BaseModel):
    """Input schema for graph execution"""
    query: str = Field(..., description="User query or prompt", min_length=1)
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Graph configuration")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class GraphOutput(BaseModel):
    """Output schema for graph execution"""
    status: str = Field(..., description="Execution status")
    result: Optional[Dict[str, Any]] = Field(None, description="Graph output")
    execution_id: Optional[str] = Field(None, description="Execution identifier")
    duration_ms: Optional[int] = Field(None, description="Execution duration in milliseconds")
    error: Optional[str] = Field(None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: int = Field(..., description="Uptime in seconds")


class ReadyResponse(BaseModel):
    """Readiness check response"""
    ready: bool = Field(..., description="Readiness status")
    checks: Dict[str, str] = Field(..., description="Component health checks")
    timestamp: str = Field(..., description="Current timestamp")


# Global state
startup_time = time.time()


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Generate request ID
    request_id = f"req_{int(start_time * 1000)}"
    
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        logger.info(
            f"Request {request_id} completed: "
            f"status={response.status_code} duration={duration:.2f}ms"
        )
        
        return response
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            f"Request {request_id} failed: {str(e)} duration={duration:.2f}ms"
        )
        raise


# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Basic health check endpoint (liveness probe).
    
    Returns basic service status without checking dependencies.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        uptime_seconds=int(time.time() - startup_time)
    )


@app.get("/ready", response_model=ReadyResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint.
    
    Checks if the service and its dependencies are ready to handle requests.
    """
    checks = {}
    ready = True
    
    # Check LangGraph API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{LANGGRAPH_API_URL}/health")
            if response.status_code == 200:
                checks["langgraph"] = "ok"
            else:
                checks["langgraph"] = f"unhealthy (status {response.status_code})"
                ready = False
    except Exception as e:
        checks["langgraph"] = f"error: {str(e)}"
        ready = False
    
    # TODO: Add checks for other dependencies (database, Redis, etc.)
    
    return ReadyResponse(
        ready=ready,
        checks=checks,
        timestamp=datetime.utcnow().isoformat()
    )


# Graph execution endpoint
@app.post("/v1/graph/run", response_model=GraphOutput, tags=["Graph"])
async def run_graph(input_data: GraphInput):
    """
    Execute a LangGraph workflow.
    
    This endpoint triggers a graph execution with the provided input
    and returns the result.
    
    Args:
        input_data: Graph input including query, user_id, session_id, etc.
    
    Returns:
        GraphOutput: Execution result including status, output, and metadata.
    
    Raises:
        HTTPException: If execution fails or times out.
    """
    start_time = time.time()
    execution_id = f"exec_{int(start_time * 1000)}"
    
    logger.info(f"Starting graph execution {execution_id}")
    
    try:
        # Prepare request to LangGraph API
        payload = {
            "input": {
                "query": input_data.query,
                "user_id": input_data.user_id or "anonymous",
                "session_id": input_data.session_id or execution_id,
                **input_data.metadata
            },
            "config": {
                "configurable": {
                    "thread_id": input_data.session_id or execution_id
                },
                **input_data.config
            }
        }
        
        # Execute graph via LangGraph API
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{LANGGRAPH_API_URL}/v1/graph/run",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    # TODO: Add authentication header if required
                    # "X-API-Key": os.getenv("LANGGRAPH_API_KEY", "")
                }
            )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Graph execution {execution_id} completed in {duration_ms}ms")
            
            return GraphOutput(
                status="success",
                result=result,
                execution_id=execution_id,
                duration_ms=duration_ms
            )
        else:
            logger.error(
                f"Graph execution {execution_id} failed: "
                f"status={response.status_code} response={response.text}"
            )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Graph execution failed: {response.text}"
            )
    
    except httpx.TimeoutException:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Graph execution {execution_id} timed out after {duration_ms}ms")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Graph execution timed out"
        )
    
    except httpx.RequestError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Graph execution {execution_id} failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to LangGraph API: {str(e)}"
        )
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Graph execution {execution_id} error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Additional endpoints can be added here
@app.get("/v1/graph/status/{execution_id}", tags=["Graph"])
async def get_execution_status(execution_id: str):
    """
    Get the status of a graph execution.
    
    TODO: Implement execution status tracking.
    """
    # This would query the execution status from LangGraph or a database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Execution status tracking not yet implemented"
    )


@app.get("/v1/graph/history", tags=["Graph"])
async def get_execution_history(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 10
):
    """
    Get execution history for a user or session.
    
    TODO: Implement execution history retrieval.
    """
    # This would query execution history from a database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Execution history not yet implemented"
    )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting RAG7 Integration API")
    logger.info(f"LangGraph API URL: {LANGGRAPH_API_URL}")
    logger.info(f"API Timeout: {API_TIMEOUT}s")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down RAG7 Integration API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=os.getenv("API_RELOAD", "false").lower() == "true"
    )
