"""
Database configuration and session management for TradeSignal.

Uses SQLAlchemy 2.0+ with async support (asyncpg driver).
Provides async engine, session factory, and FastAPI dependency.
"""

import asyncio
import logging
import os
import socket
import ssl
import time
from typing import AsyncGenerator
from contextlib import asynccontextmanager

import certifi

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import (  # type: ignore[import-untyped]
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base  # type: ignore[import-untyped]
from sqlalchemy.pool import NullPool, QueuePool  # type: ignore[import-untyped]
from sqlalchemy import text  # type: ignore[import-untyped]
from sqlalchemy.exc import SQLAlchemyError  # type: ignore[import-untyped]

from app.config import settings
from app.utils.dns_resolver import resolve_database_url, DNSResolutionError

# Configure logging
logger = logging.getLogger(__name__)

# Constants for SSL error detection
SSL_ERROR_TERMS = ['ssl', 'certificate', 'cert', 'tls', 'certificate verify', 'sslcertverificationerror']

# Configure SQLAlchemy loggers to reduce verbosity
# Only show warnings/errors, not all SQL queries
# This prevents duplicate/verbose SQL query logs in production
# Set SQLALCHEMY_LOG_LEVEL=DEBUG in .env if you need to see all SQL queries
# Set SQLALCHEMY_ECHO=true in .env if you need SQL query logging (requires DEBUG log level)
sqlalchemy_log_level = os.getenv("SQLALCHEMY_LOG_LEVEL", "WARNING").upper()
sqlalchemy_log_level_value = getattr(logging, sqlalchemy_log_level, logging.WARNING)

# Configure all SQLAlchemy loggers to reduce noise
# This must be done before any SQLAlchemy engine is created
for logger_name in ["sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.dialects", "sqlalchemy.orm"]:
    sqlalchemy_logger = logging.getLogger(logger_name)
    sqlalchemy_logger.setLevel(sqlalchemy_log_level_value)
    # Prevent propagation to root logger to avoid duplicate logs
    sqlalchemy_logger.propagate = True  # Keep propagation but control level

# Declarative Base for SQLAlchemy models
Base = declarative_base()


class DatabaseManager:
    """
    Manages database engine and session lifecycle.
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._database_available: bool = False  # Track database availability
        self._last_connection_attempt: float = 0  # Timestamp of last connection attempt
        self._resolved_database_url: str | None = None  # Cached resolved URL

    def _resolve_database_url(self) -> str:
        """Resolve database URL with DNS resolution."""
        try:
            if self._resolved_database_url is None:
                logger.info("Resolving database URL hostname...")
                self._resolved_database_url = resolve_database_url(settings.database_url_async)
                logger.info("✅ Database URL resolved successfully")
            return self._resolved_database_url
        except DNSResolutionError as dns_error:
            logger.error(f"❌ DNS resolution failed: {dns_error}")
            logger.warning("⚠️  Cannot create database engine - DNS resolution failed")
            self._database_available = False
            raise
        except Exception as dns_error:
            logger.error(f"❌ Unexpected error during DNS resolution: {dns_error}")
            # Fall back to original URL if DNS resolution fails unexpectedly
            return settings.database_url_async

    def _is_supabase_connection(self) -> bool:
        """Check if this is a Supabase connection."""
        return "supabase.com" in settings.database_url or "supabase.co" in settings.database_url

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create and configure SSL context for Supabase connections."""
        # Use certifi's CA bundle to ensure proper certificate verification
        # This is especially important in production environments like Render
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        # Explicitly set minimum protocol version to TLS 1.2 for security (S4423)
        if hasattr(ssl, 'PROTOCOL_TLS_CLIENT'):
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        # Explicitly enable hostname verification (S5527)
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Allow disabling SSL verification when explicitly enabled via environment variable
        disable_ssl_verification_env = os.getenv("DISABLE_SSL_VERIFICATION", "false").lower()
        disable_ssl_verification = disable_ssl_verification_env == "true"

        logger.debug(
            f"SSL configuration check: DISABLE_SSL_VERIFICATION={disable_ssl_verification_env}, "
            f"environment={settings.environment}, will_disable={disable_ssl_verification}"
        )

        if disable_ssl_verification:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.warning(
                f"⚠️  SSL certificate verification DISABLED (environment={settings.environment}). "
                "This may be needed for corporate proxies or certificate chain issues with Supabase. "
                "Only use this if you trust the network connection."
            )
        else:
            if settings.environment == "production":
                logger.info("SSL configured for Supabase with full certificate verification (production mode)")
            else:
                logger.info("SSL configured for Supabase with certificate verification enabled")
        
        return ssl_context

    def _build_connect_args(self, is_supabase: bool) -> dict:
        """Build connection arguments for database engine."""
        connect_args = {
            "command_timeout": 60,
            "server_settings": {
                "application_name": "tradesignal_backend"
            },
            "timeout": 30,
        }
        
        if is_supabase:
            connect_args["ssl"] = self._create_ssl_context()
            connect_args["statement_cache_size"] = 0
            logger.info("SSL configured for Supabase (statement cache disabled for pooler compatibility)")
        
        return connect_args

    def _determine_pool_class(self, is_supabase: bool) -> type:
        """Determine the appropriate pool class based on database type and environment."""
        if is_supabase:
            return NullPool
        return NullPool if settings.environment == "testing" else QueuePool

    def _build_engine_args(
        self, 
        pool_class: type, 
        connect_args: dict, 
        is_supabase: bool
    ) -> dict:
        """Build engine arguments for SQLAlchemy engine creation."""
        echo_enabled = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
        pool_recycle_time = 60 if is_supabase else 3600
        
        engine_args = {
            "echo": echo_enabled,
            "pool_pre_ping": False if is_supabase else True,
            "poolclass": pool_class,
            "connect_args": connect_args,
        }
        
        if pool_class != NullPool:
            pool_size = 3 if is_supabase else 10
            max_overflow = 5 if is_supabase else 20
            engine_args["pool_size"] = pool_size
            engine_args["max_overflow"] = max_overflow
            engine_args["pool_recycle"] = pool_recycle_time
            engine_args["pool_timeout"] = 30
        
        return engine_args

    def _create_engine_with_error_handling(
        self, 
        database_url: str, 
        engine_args: dict
    ) -> AsyncEngine:
        """Create async engine with error handling."""
        try:
            engine = create_async_engine(database_url, **engine_args)
            logger.info(f"Database engine created successfully (environment: {settings.environment})")
            return engine
        except Exception as engine_error:
            error_str = str(engine_error).lower()
            if any(ssl_term in error_str for ssl_term in SSL_ERROR_TERMS):
                logger.error(
                    f"Database engine creation failed with SSL error: {engine_error}\n"
                    "If you're behind a corporate proxy or experiencing certificate chain issues, "
                    "set DISABLE_SSL_VERIFICATION=true in your .env file (development/testing only)."
                )
            raise

    def get_engine(self) -> AsyncEngine:
        if self._engine is None:
            try:
                database_url = self._resolve_database_url()
                is_supabase = self._is_supabase_connection()
                connect_args = self._build_connect_args(is_supabase)
                pool_class = self._determine_pool_class(is_supabase)
                
                if is_supabase:
                    logger.info("Using Supabase-optimized configuration (NullPool for Session mode compatibility, no statement cache)")
                
                engine_args = self._build_engine_args(pool_class, connect_args, is_supabase)
                self._engine = self._create_engine_with_error_handling(database_url, engine_args)
                self._database_available = True
            except DNSResolutionError:
                self._database_available = False
                raise
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                self._database_available = False
                raise

        return self._engine

    @property
    def is_available(self) -> bool:
        """
        Check if database is currently available.

        Returns:
            bool: True if database connection is available, False otherwise
        """
        return self._database_available

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._session_factory

    async def _handle_session_error(self, e: Exception, session: AsyncSession | None) -> None:
        """Handle errors in database session with appropriate logging."""
        if session:
            await session.rollback()
        
        error_str = str(e).lower()
        is_ssl_error = any(ssl_term in error_str for ssl_term in SSL_ERROR_TERMS)
        
        if is_ssl_error:
            logger.error(
                f"Database SSL error: {e}\n"
                "If you're behind a corporate proxy or experiencing certificate chain issues, "
                "set DISABLE_SSL_VERIFICATION=true in your .env file (development/testing only)."
            )
        elif isinstance(e, SQLAlchemyError):
            logger.error(f"Database session error: {e}")
        else:
            logger.error(f"Unexpected error in database session: {e}")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        session_factory = self.get_session_factory()
        session = None
        try:
            session = session_factory()
            yield session
            await session.commit()
        except HTTPException:
            # Don't rollback or log for HTTP exceptions - these are expected auth errors, etc.
            if session:
                await session.rollback()
            raise
        except (SQLAlchemyError, Exception) as e:
            await self._handle_session_error(e, session)
            raise
        finally:
            # CRITICAL: Always close session to release connection back to pool (or close for NullPool)
            if session:
                await session.close()

    def _handle_dns_error(self, error: Exception) -> bool:
        """Handle DNS resolution errors."""
        logger.error(f"Database connection check failed (DNS): {error}")
        logger.error("  -> DNS resolution failed. Check network connectivity and DNS settings.")
        self._database_available = False
        return False

    def _handle_prepared_statement_error(self, error_str: str) -> bool:
        """Handle prepared statement errors gracefully."""
        logger.warning(
            f"Database connection check: Prepared statement conflict detected. "
            f"This is expected with pgbouncer in transaction mode. "
            f"Connection may still work for actual queries. Error: {error_str}"
        )
        self._database_available = True
        return True

    def _handle_ssl_error(self, error_str: str, error_type_name: str | None = None) -> bool:
        """Handle SSL-related errors."""
        logger.error(f"Database connection check failed (SSL): {error_str}")
        if error_type_name:
            logger.error(f"Error type: {error_type_name}")
        logger.error(
            "  -> SSL certificate verification failed. This often happens when:\n"
            "     - Behind a corporate proxy that intercepts SSL connections\n"
            "     - Using a VPN with SSL inspection\n"
            "     - Certificate chain issues with the database provider\n"
            "  -> For development/testing, you can disable SSL verification by setting:\n"
            "     DISABLE_SSL_VERIFICATION=true in your .env file\n"
            "  -> WARNING: This is NOT secure for production environments!"
        )
        self._database_available = False
        return False

    def _handle_sqlalchemy_error(self, e: SQLAlchemyError) -> bool:
        """Handle SQLAlchemy-specific errors."""
        error_str = str(e)
        error_lower = error_str.lower()
        
        if "DuplicatePreparedStatementError" in error_str or "prepared statement" in error_lower:
            return self._handle_prepared_statement_error(error_str)
        
        if any(ssl_term in error_lower for ssl_term in SSL_ERROR_TERMS):
            return self._handle_ssl_error(error_str)
        
        logger.error(f"Database connection check failed (SQLAlchemyError): {error_str}")
        if "authentication" in error_lower or "password" in error_lower:
            logger.error("  -> Authentication failed: Check username/password in DATABASE_URL")
        elif "does not exist" in error_lower:
            logger.error("  -> Database does not exist: Check database name in DATABASE_URL")
        elif "could not connect" in error_lower or "connection refused" in error_lower:
            logger.error("  -> Connection refused: Check if database server is running and host/port are correct")
        elif "gaierror" in error_lower or "getaddrinfo" in error_lower:
            logger.error("  -> DNS resolution failed: Check network connectivity and DNS settings")
        
        self._database_available = False
        return False

    def _handle_connection_exception(self, e: Exception) -> bool:
        """Handle general exceptions during connection check."""
        error_str = str(e)
        error_lower = error_str.lower()
        error_type_name = type(e).__name__
        
        if "DuplicatePreparedStatementError" in error_str or "prepared statement" in error_lower:
            return self._handle_prepared_statement_error(error_str)
        
        if any(ssl_term in error_lower for ssl_term in SSL_ERROR_TERMS):
            return self._handle_ssl_error(error_str, error_type_name)
        
        if "gaierror" in error_lower or "getaddrinfo" in error_lower:
            return self._handle_dns_error(e)
        
        logger.error(f"Unexpected error during connection check: {error_str}")
        logger.error(f"Error type: {error_type_name}")
        self._database_available = False
        return False

    async def _test_connection_with_timeout(self, engine: AsyncEngine) -> bool:
        """Test database connection with timeout protection."""
        async def _connect_and_test():
            conn = None
            try:
                conn = await engine.connect()
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()
                return True
            finally:
                if conn:
                    await conn.close()
        
        try:
            result = await asyncio.wait_for(_connect_and_test(), timeout=30.0)
            if result:
                logger.info("Database connection check: OK")
                self._database_available = True
            else:
                self._database_available = False
            return result
        except asyncio.TimeoutError:
            logger.warning("Database connection check timed out after 30s")
            self._database_available = False
            return False

    async def check_connection(self) -> bool:
        """
        Test database connectivity.

        Returns:
            bool: True if connection successful, False otherwise

        Used by health check endpoint to verify database status.
        Updates the _database_available flag based on connection status.

        Note: Uses raw SQL execution without prepared statements to avoid
        DuplicatePreparedStatementError with pgbouncer in transaction mode.
        """
        self._last_connection_attempt = time.time()

        try:
            engine = self.get_engine()
            return await self._test_connection_with_timeout(engine)
        except asyncio.CancelledError:
            logger.warning("Database connection check was cancelled")
            self._database_available = False
            raise
        except (DNSResolutionError, socket.gaierror) as dns_error:
            return self._handle_dns_error(dns_error)
        except SQLAlchemyError as e:
            return self._handle_sqlalchemy_error(e)
        except Exception as e:
            return self._handle_connection_exception(e)

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_manager.get_session() as session:
            yield session
    except HTTPException:
        # Re-raise HTTP exceptions as-is (these are expected auth errors, etc.)
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_db: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable.",
        )

async def init_db() -> None:
    try:
        engine = db_manager.get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise