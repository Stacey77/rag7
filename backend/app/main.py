"""Main FastAPI application for the Agentic Agent platform."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.api import auth, decisions, oversight_ws, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print("Starting Agentic Agent Platform...")
    
    # Initialize database (create tables if needed)
    # In production, migrations should be run separately
    # await init_db()
    
    print("Application started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down Agentic Agent Platform...")


# Create FastAPI app
app = FastAPI(
    title="Agentic Agent Platform",
    description="Production-ready agentic AI platform with oversight and RBAC",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(decisions.router)
app.include_router(oversight_ws.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Agentic Agent Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "agentic-platform"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
