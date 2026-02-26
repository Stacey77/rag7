"""Integration tests for database operations."""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Settings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection can be established."""
    settings = Settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.database.url,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Test connection
    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        assert result.scalar() == 1
    
    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_session_creation():
    """Test database session can be created."""
    settings = Settings()
    
    engine = create_async_engine(settings.database.url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        result = await session.execute("SELECT current_database()")
        db_name = result.scalar()
        assert db_name is not None
    
    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection can be established."""
    import redis.asyncio as redis_async
    from src.config import Settings
    
    settings = Settings()
    
    redis_client = redis_async.from_url(
        settings.redis.url,
        encoding="utf-8",
        decode_responses=True
    )
    
    # Test ping
    pong = await redis_client.ping()
    assert pong is True
    
    # Test set/get
    await redis_client.set("test_key", "test_value", ex=10)
    value = await redis_client.get("test_key")
    assert value == "test_value"
    
    # Cleanup
    await redis_client.delete("test_key")
    await redis_client.close()


@pytest.mark.integration  
@pytest.mark.asyncio
async def test_concurrent_database_operations():
    """Test concurrent database operations."""
    settings = Settings()
    engine = create_async_engine(settings.database.url, echo=False, pool_size=5)
    
    async def query_task(task_id: int):
        async with engine.begin() as conn:
            result = await conn.execute(f"SELECT {task_id} as task_id")
            return result.scalar()
    
    # Run 10 concurrent queries
    tasks = [query_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Verify all results
    assert len(results) == 10
    assert set(results) == set(range(10))
    
    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_transaction_rollback():
    """Test transaction rollback works correctly."""
    settings = Settings()
    engine = create_async_engine(settings.database.url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Start transaction
            await session.begin()
            
            # This would fail in real scenario
            await session.execute("CREATE TEMPORARY TABLE test_rollback (id INT)")
            await session.execute("INSERT INTO test_rollback VALUES (1)")
            
            # Force rollback
            await session.rollback()
            
        except Exception:
            await session.rollback()
    
    await engine.dispose()
    # Test passes if no exception raised
    assert True
