"""FastAPI application main entry point."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from app.core import get_settings
from app.db.session import engine, async_session_maker
from app.db.base import Base
from app.api import decisions, oversight_ws, auth, admin


settings = get_settings()

# Redis connection pool
redis_pool: redis.Redis | None = None


async def init_redis():
    """Initialize Redis connection pool."""
    global redis_pool
    redis_pool = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    return redis_pool


async def close_redis():
    """Close Redis connection pool."""
    global redis_pool
    if redis_pool:
        await redis_pool.close()


def get_redis() -> redis.Redis:
    """Get Redis connection."""
    if redis_pool is None:
        raise RuntimeError("Redis pool not initialized")
    return redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_redis()
    
    # Create tables (for development; use migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic Agent Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(decisions.router, prefix=f"{settings.API_V1_PREFIX}/decisions", tags=["decisions"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"])
app.include_router(oversight_ws.router, prefix=f"{settings.API_V1_PREFIX}/oversight", tags=["oversight"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agentic Agent Platform API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
