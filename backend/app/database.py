"""
Database configuration and session management for TradeSignal.

Uses SQLAlchemy 2.0+ with async support (asyncpg driver).
Provides async engine, session factory, and FastAPI dependency.
"""

import logging
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Declarative Base for SQLAlchemy models
# Import this in model files: from app.database import Base
Base = declarative_base()


class DatabaseManager:
    """
    Manages database engine and session lifecycle.

    Provides async engine creation, session factory, and connection testing.
    """

    def __init__(self) -> None:
        """Initialize database manager with engine and session factory."""
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def get_engine(self) -> AsyncEngine:
        """
        Get or create async database engine.

        Returns:
            AsyncEngine: SQLAlchemy async engine instance

        Configuration:
            - Uses asyncpg driver for PostgreSQL
            - Connection pooling with configurable size
            - SQL echo in development mode
            - Proper error handling
        """
        if self._engine is None:
            try:
                # Determine pool class based on environment
                pool_class = (
                    NullPool if settings.environment == "testing" else QueuePool
                )

                # Create async engine with asyncpg driver
                self._engine = create_async_engine(
                    settings.database_url_async,
                    echo=settings.debug,  # Log SQL queries in debug mode
                    pool_pre_ping=True,  # Verify connections before using
                    pool_size=10,  # Number of persistent connections to maintain
                    max_overflow=20,  # Allow additional burst connections when pool is full
                    pool_recycle=3600,  # Recycle connections after 1 hour
                    pool_timeout=30,  # Wait max 30 seconds for connection from pool
                    poolclass=pool_class,
                    connect_args={
                        "command_timeout": 10,  # 10 second timeout for SQL commands
                        "server_settings": {
                            "application_name": "tradesignal_backend"
                        },
                        "timeout": 10,  # Connection establishment timeout (10 seconds)
                    },
                )
                logger.info(
                    f"Database engine created successfully (environment: {settings.environment})"
                )
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise

        return self._engine

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Get or create session factory.

        Returns:
            async_sessionmaker: Factory for creating database sessions
        """
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,  # Don't expire objects after commit
                autocommit=False,  # Manual transaction control
                autoflush=False,  # Manual flush control
            )
            logger.info("Database session factory created successfully")

        return self._session_factory

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for database sessions.

        Yields:
            AsyncSession: Database session with automatic cleanup

        Usage:
            async with db_manager.get_session() as session:
                result = await session.execute(query)
        """
        session_factory = self.get_session_factory()
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    async def check_connection(self) -> bool:
        """
        Test database connectivity.

        Returns:
            bool: True if connection successful, False otherwise

        Used by health check endpoint to verify database status.
        """
        try:
            import asyncio
            engine = self.get_engine()
            
            # Create a connection with timeout protection
            async def _connect_and_test():
                conn = await engine.connect()
                try:
                await conn.execute(text("SELECT 1"))
                    return True
                finally:
                    await conn.close()
            
            # Wrap the entire operation in a timeout
            try:
                result = await asyncio.wait_for(_connect_and_test(), timeout=4.0)
                if result:
            logger.info("Database connection check: OK")
                return result
            except asyncio.TimeoutError:
                logger.warning("Database connection check timed out after 4s")
                return False
        except asyncio.CancelledError:
            logger.warning("Database connection check was cancelled")
            raise  # Re-raise CancelledError so it can be handled upstream
        except SQLAlchemyError as e:
            logger.error(f"Database connection check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection check: {e}")
            return False

    async def close(self) -> None:
        """
        Close database engine and cleanup connections.

        Should be called during application shutdown.
        """
        if self._engine is not None:
            try:
                # Dispose engine with timeout to prevent hanging
                import asyncio
                # For async engines, dispose() is async
                await asyncio.wait_for(
                    self._engine.dispose(),
                    timeout=3.0
                )
                logger.info("Database engine closed successfully")
            except asyncio.TimeoutError:
                logger.warning("Database engine dispose timed out, forcing close")
            except Exception as e:
                logger.error(f"Error closing database engine: {e}")
            finally:
                self._engine = None
                self._session_factory = None


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session for request handling

    Usage in FastAPI routes:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Features:
        - Automatic session creation per request
        - Automatic commit on success
        - Automatic rollback on error
        - Automatic cleanup after request
        - Proper error handling for connection failures
    """
    try:
        session_factory = db_manager.get_session_factory()
    except Exception as e:
        logger.error(f"Failed to get session factory: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later.",
        )

    session = None
    try:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as db_error:
                await session.rollback()
                logger.error(f"Database transaction error: {db_error}", exc_info=True)
                # Re-raise to let route handlers deal with it
                raise
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Unexpected error in database transaction: {e}", exc_info=True
                )
                raise
            finally:
                if session:
                    await session.close()
    except HTTPException:
        # Allow HTTPException (like 401 Unauthorized) to propagate without modification
        # This ensures authentication errors return proper status codes instead of 500
        raise
    except (TimeoutError, asyncio.TimeoutError) as timeout_error:
        # Handle connection timeout errors specifically
        logger.error(
            f"Database connection timeout in get_db: {timeout_error}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection timeout. Please try again later.",
        )
    except asyncio.CancelledError as cancelled_error:
        # Handle cancelled connections that lead to timeout errors
        logger.error(
            f"Database connection cancelled in get_db (likely timeout): {cancelled_error}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection timeout. Please try again later.",
        )
    except SQLAlchemyError as db_error:
        # Check if the underlying error is a timeout
        error_str = str(db_error).lower()
        if "timeout" in error_str or "timed out" in error_str:
            logger.error(
                f"Database connection timeout (via SQLAlchemy): {db_error}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection timeout. Please try again later.",
            )
        logger.error(f"Database connection error in get_db: {db_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection error. Please try again later.",
        )
    except Exception as e:
        # Check if the underlying error is a timeout
        error_str = str(e).lower()
        if "timeout" in error_str or "timed out" in error_str:
            logger.error(
                f"Database connection timeout (unexpected): {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection timeout. Please try again later.",
            )
        logger.error(f"Unexpected error in get_db: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in SQLAlchemy models.
    Should be called during application startup.

    Note: In production, use Alembic migrations instead.
    """
    try:
        engine = db_manager.get_engine()
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise


async def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use in development/testing environments.
    """
    if settings.is_production:
        raise RuntimeError("Cannot drop database in production environment")

    try:
        engine = db_manager.get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise
