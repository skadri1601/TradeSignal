"""
Pytest configuration and fixtures for TradeSignal tests.
Phase 6: Testing infrastructure.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db

# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session.

    Uses in-memory SQLite for fast, isolated tests.
    Database is created fresh for each test function.
    """
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create session
    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db: AsyncSession):
    """
    Create FastAPI test client.

    Overrides the database dependency to use test database.
    """
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis cache for testing."""
    class MockRedis:
        def __init__(self):
            self.data = {}

        def enabled(self):
            return True

        def get(self, key):
            return self.data.get(key)

        def set(self, key, value, ttl=None):
            self.data[key] = value

        def delete(self, key):
            self.data.pop(key, None)

        def exists(self, key):
            return key in self.data

    mock = MockRedis()
    monkeypatch.setattr("app.core.redis_cache.get_cache", lambda: mock)
    return mock
