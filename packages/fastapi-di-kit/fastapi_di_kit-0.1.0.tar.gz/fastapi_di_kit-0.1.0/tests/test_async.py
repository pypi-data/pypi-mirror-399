"""Tests for async service support."""

import pytest
import asyncio
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi_di_kit import service, Inject, setup_di_middleware, Lifecycle, DIContainer


class AsyncDatabase:
    """Async database service for testing."""
    
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        """Simulate async connection."""
        await asyncio.sleep(0.01)  # Simulate I/O
        self.connected = True
    
    async def query(self, sql: str) -> str:
        """Simulate async query."""
        await asyncio.sleep(0.01)
        return f"result: {sql}"


class AsyncUserService:
    """Async service with async methods."""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
    
    async def get_user(self, user_id: int) -> dict:
        """Get user asynchronously."""
        result = await self.db.query(f"SELECT * FROM users WHERE id={user_id}")
        return {"id": user_id, "data": result}


class SyncServiceWithAsyncDependency:
    """Sync service that has async dependency."""
    
    def __init__(self, async_db: AsyncDatabase):
        self.db = async_db
    
    def get_status(self) -> str:
        return "connected" if self.db.connected else "disconnected"


@pytest.mark.asyncio
async def test_async_service_resolution():
    """Test that async services can be resolved."""
    container = DIContainer()
    
    container.register(AsyncDatabase)
    
    db = container.resolve(AsyncDatabase)
    
    assert isinstance(db, AsyncDatabase)
    assert not db.connected
    
    await db.connect()
    assert db.connected


@pytest.mark.asyncio
async def test_async_service_with_dependencies():
    """Test async service with dependencies."""
    container = DIContainer()
    
    container.register(AsyncDatabase)
    container.register(AsyncUserService)
    
    service = container.resolve(AsyncUserService)
    
    assert isinstance(service, AsyncUserService)
    assert isinstance(service.db, AsyncDatabase)
    
    await service.db.connect()
    user = await service.get_user(1)
    
    assert user["id"] == 1
    assert "result:" in user["data"]


def test_async_factory_limitation():
    """Test that demonstrates async factories are not yet supported."""
    container = DIContainer()
    
    # Sync factory that creates async service
    def create_async_db() -> AsyncDatabase:
        db = AsyncDatabase()
        # Cannot await here in sync factory
        return db
    
    container.register(AsyncDatabase, factory=create_async_db)
    
    db = container.resolve(AsyncDatabase)
    
    assert isinstance(db, AsyncDatabase)
    # Note: db is not connected because factory is sync


def test_sync_service_with_async_dependency():
    """Test sync service can have async dependency."""
    container = DIContainer()
    
    container.register(AsyncDatabase)
    container.register(SyncServiceWithAsyncDependency)
    
    service = container.resolve(SyncServiceWithAsyncDependency)
    
    assert isinstance(service, SyncServiceWithAsyncDependency)
    assert isinstance(service.db, AsyncDatabase)


@pytest.mark.asyncio
async def test_async_in_fastapi_route():
    """Test async services in FastAPI async routes."""
    app = FastAPI()
    setup_di_middleware(app)
    
    @service()
    class AsyncCounter:
        def __init__(self):
            self.count = 0
        
        async def increment(self) -> int:
            await asyncio.sleep(0.01)
            self.count += 1
            return self.count
    
    @app.get("/count")
    async def get_count(counter: AsyncCounter = Depends(Inject[AsyncCounter])):
        count = await counter.increment()
        return {"count": count}
    
    client = TestClient(app)
    
    response = client.get("/count")
    assert response.status_code == 200
    assert response.json() == {"count": 1}


@pytest.mark.asyncio
async def test_async_scoped_services():
    """Test async services with scoped lifecycle."""
    container = DIContainer()
    
    @service(lifecycle=Lifecycle.SCOPED)
    class AsyncRequestContext:
        def __init__(self):
            self.request_id = id(self)
            self.data = None
        
        async def load_data(self):
            await asyncio.sleep(0.01)
            self.data = "loaded"
    
    container.register(AsyncRequestContext, lifecycle=Lifecycle.SCOPED)
    
    with container.request_scope():
        ctx1 = container.resolve(AsyncRequestContext)
        ctx2 = container.resolve(AsyncRequestContext)
        
        assert ctx1 is ctx2
        
        await ctx1.load_data()
        assert ctx2.data == "loaded"


@pytest.mark.asyncio
async def test_async_multiple_dependencies():
    """Test async service with multiple async dependencies."""
    container = DIContainer()
    
    class AsyncCache:
        async def get(self, key: str) -> str:
            await asyncio.sleep(0.01)
            return f"cached_{key}"
    
    class AsyncLogger:
        async def log(self, message: str):
            await asyncio.sleep(0.01)
    
    class AsyncService:
        def __init__(self, cache: AsyncCache, logger: AsyncLogger):
            self.cache = cache
            self.logger = logger
        
        async def process(self, key: str) -> str:
            await self.logger.log(f"Processing {key}")
            result = await self.cache.get(key)
            return result
    
    container.register(AsyncCache)
    container.register(AsyncLogger)
    container.register(AsyncService)
    
    service = container.resolve(AsyncService)
    result = await service.process("test")
    
    assert result == "cached_test"


@pytest.mark.asyncio
async def test_async_singleton_lifecycle():
    """Test async services with singleton lifecycle."""
    container = DIContainer()
    
    container.register(AsyncDatabase, lifecycle=Lifecycle.SINGLETON)
    
    db1 = container.resolve(AsyncDatabase)
    db2 = container.resolve(AsyncDatabase)
    
    assert db1 is db2
    
    await db1.connect()
    
    # Both references should show connected
    assert db2.connected


@pytest.mark.asyncio
async def test_async_transient_lifecycle():
    """Test async services with transient lifecycle."""
    container = DIContainer()
    
    container.register(AsyncDatabase, lifecycle=Lifecycle.TRANSIENT)
    
    db1 = container.resolve(AsyncDatabase)
    db2 = container.resolve(AsyncDatabase)
    
    assert db1 is not db2
    
    await db1.connect()
    
    # Only db1 should be connected
    assert db1.connected
    assert not db2.connected


def test_async_service_in_sync_fastapi_route():
    """Test that async services work in sync routes too."""
    app = FastAPI()
    setup_di_middleware(app)
    
    @service()
    class SimpleAsyncService:
        def __init__(self):
            self.value = "test"
    
    @app.get("/value")
    def get_value(service: SimpleAsyncService = Depends(Inject[SimpleAsyncService])):
        return {"value": service.value}
    
    client = TestClient(app)
    
    response = client.get("/value")
    assert response.status_code == 200
    assert response.json() == {"value": "test"}
