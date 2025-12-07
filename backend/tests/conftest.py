"""
Pytest configuration and fixtures for TradeSignal tests.
Phase 6: Testing infrastructure.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.core.security import get_current_active_user
# Import all models to ensure they are registered with Base.metadata
from app.models import *  # noqa: F401, F403

# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session.

    Uses in-memory SQLite for fast, isolated tests.
    Database is created fresh for each test function.
    """
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
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


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user for authentication."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$dummy",  # Dummy hash for testing
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def client(test_db: AsyncSession):
    """
    Create FastAPI test client.

    Overrides the database dependency to use test database.
    Overrides authentication to use a mock user.
    """
    async def override_get_db():
        yield test_db

    # Create a mock user for authentication
    # We'll create it synchronously since TestClient is sync
    mock_user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$dummy",
        is_active=True,
        is_verified=True
    )

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_user

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
