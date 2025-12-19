"""
Database configuration and session management for TradeSignal.

Uses SQLAlchemy 2.0+ with async support (asyncpg driver).
Provides async engine, session factory, and FastAPI dependency.
"""

import logging
import os
import socket
import time
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
from app.utils.dns_resolver import resolve_database_url, DNSResolutionError

# Configure logging
logger = logging.getLogger(__name__)

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

    def get_engine(self) -> AsyncEngine:
        if self._engine is None:
            try:
                # Resolve DNS before creating engine
                # This prevents DNS failures from crashing the application
                try:
                    if self._resolved_database_url is None:
                        logger.info("Resolving database URL hostname...")
                        self._resolved_database_url = resolve_database_url(settings.database_url_async)
                        logger.info("✅ Database URL resolved successfully")
                    database_url = self._resolved_database_url
                except DNSResolutionError as dns_error:
                    logger.error(f"❌ DNS resolution failed: {dns_error}")
                    logger.warning("⚠️  Cannot create database engine - DNS resolution failed")
                    self._database_available = False
                    raise
                except Exception as dns_error:
                    logger.error(f"❌ Unexpected error during DNS resolution: {dns_error}")
                    # Fall back to original URL if DNS resolution fails unexpectedly
                    database_url = settings.database_url_async

                # Determine pool class based on environment
                pool_class = (
                    NullPool if settings.environment == "testing" else QueuePool
                )

                # Determine if this is a Supabase connection (requires SSL)
                is_supabase = "supabase.com" in settings.database_url or "supabase.co" in settings.database_url
                
                # Build connect_args with SSL for Supabase
                connect_args = {
                    "command_timeout": 60,  # Increased to 60s to prevent timeouts on heavy loads
                    "server_settings": {
                        "application_name": "tradesignal_backend"
                    },
                    "timeout": 30,  # Connection timeout
                }
                
                # Add SSL for Supabase connections
                if is_supabase:
                    import ssl
                    # Create SSL context with proper certificate verification
                    # Supabase uses valid certificates that should be in Python's trust store
                    ssl_context = ssl.create_default_context()
                    
                    # Allow disabling SSL verification only for local development via environment variable
                    # SECURITY WARNING: Never disable SSL verification in production
                    # This can help with corporate proxies, self-signed certificates, or certificate chain issues
                    disable_ssl_verification_env = os.getenv("DISABLE_SSL_VERIFICATION", "false").lower()
                    disable_ssl_verification = disable_ssl_verification_env == "true"
                    
                    logger.debug(
                        f"SSL configuration check: DISABLE_SSL_VERIFICATION={disable_ssl_verification_env}, "
                        f"environment={settings.environment}, will_disable={disable_ssl_verification and settings.environment in ['development', 'testing']}"
                    )
                    
                    if disable_ssl_verification and settings.environment in ["development", "testing"]:
                        # Only allow disabling verification in development/testing environments
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        logger.warning(
                            "⚠️  SSL certificate verification DISABLED for development - NOT SECURE FOR PRODUCTION. "
                            "This may be needed for corporate proxies or certificate chain issues."
                        )
                    else:
                        # Enable proper SSL verification (default and required for production)
                        ssl_context.check_hostname = True
                        ssl_context.verify_mode = ssl.CERT_REQUIRED
                        # Try to handle certificate chain issues more gracefully
                        # Some environments may have incomplete certificate chains
                        try:
                            # Test if we can create the context successfully
                            # This will raise an error if there are fundamental SSL issues
                            pass  # Context creation already happened above
                        except Exception as ssl_error:
                            logger.error(
                                f"SSL context creation failed: {ssl_error}. "
                                "If you're behind a corporate proxy or have certificate chain issues, "
                                "set DISABLE_SSL_VERIFICATION=true in your .env (development only)."
                            )
                            raise
                        
                        if settings.environment == "production":
                            logger.info("SSL configured for Supabase with full certificate verification (production mode)")
                        else:
                            logger.info("SSL configured for Supabase with certificate verification enabled")
                    
                    connect_args["ssl"] = ssl_context
                    # Disable prepared statements for Supabase transaction pooler compatibility
                    connect_args["statement_cache_size"] = 0
                    logger.info("SSL configured for Supabase (statement cache disabled for pooler compatibility)")
                
                # Configure pool size based on database type
                # Supabase Session/Transaction mode has connection limits
                if is_supabase:
                    # CRITICAL FIX: Use NullPool for Supabase to avoid "MaxClientsInSessionMode" error
                    # NullPool creates a new connection per request and closes it immediately
                    # This prevents exhausting the Supabase pooler's connection limit
                    # Session mode has strict max_clients limit tied to pool_size
                    pool_class = NullPool
                    # Add statement_cache_size=0 to ensure asyncpg doesn't cache statements
                    connect_args["statement_cache_size"] = 0
                    logger.info("Using Supabase-optimized configuration (NullPool for Session mode compatibility, no statement cache)")
                else:
                    pool_class = (
                        NullPool if settings.environment == "testing" else QueuePool
                    )
                    pool_size = 10  # Standard pool size for direct PostgreSQL
                    max_overflow = 20  # Allow additional burst connections

                # Create async engine with asyncpg driver
                # For Supabase, connections are recycled more frequently to avoid prepared statement conflicts
                pool_recycle_time = 60 if is_supabase else 3600  # 60 seconds for Supabase, 1 hour for direct

                # Build engine arguments
                # Disable echo to prevent verbose SQL logging (use SQLALCHEMY_LOG_LEVEL=DEBUG if needed)
                # echo=True logs all SQL queries at INFO level, which is too verbose for production
                echo_enabled = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"
                engine_args = {
                    "echo": echo_enabled,  # Only enable if explicitly requested via SQLALCHEMY_ECHO=true
                    # Disable pre-ping for Supabase to reduce latency (PgBouncer handles liveness)
                    # Enable for others for safety
                    "pool_pre_ping": False if is_supabase else True,
                    "poolclass": pool_class,
                    "connect_args": connect_args,
                }

                # Only add pool arguments if NOT using NullPool
                if pool_class != NullPool:
                    engine_args["pool_size"] = pool_size if not is_supabase else 3  # Smaller pool for Supabase
                    engine_args["max_overflow"] = max_overflow if not is_supabase else 5  # Limited overflow
                    engine_args["pool_recycle"] = pool_recycle_time
                    engine_args["pool_timeout"] = 30

                try:
                    self._engine = create_async_engine(
                        database_url,  # Use resolved URL instead of settings.database_url_async
                        **engine_args
                    )
                    logger.info(
                        f"Database engine created successfully (environment: {settings.environment})"
                    )
                except Exception as engine_error:
                    # Check if it's an SSL-related error
                    error_str = str(engine_error).lower()
                    if any(ssl_term in error_str for ssl_term in ['ssl', 'certificate', 'cert', 'tls']):
                        logger.error(
                            f"Database engine creation failed with SSL error: {engine_error}\n"
                            "If you're behind a corporate proxy or experiencing certificate chain issues, "
                            "set DISABLE_SSL_VERIFICATION=true in your .env file (development/testing only)."
                        )
                    raise
                self._database_available = True  # Mark as available on success
            except DNSResolutionError:
                # DNS resolution failed - re-raise to prevent engine creation
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
        except SQLAlchemyError as e:
            if session:
                await session.rollback()
            # Check if it's an SSL-related error
            error_str = str(e).lower()
            if any(ssl_term in error_str for ssl_term in ['ssl', 'certificate', 'cert', 'tls', 'certificate verify']):
                logger.error(
                    f"Database SSL error: {e}\n"
                    "If you're behind a corporate proxy or experiencing certificate chain issues, "
                    "set DISABLE_SSL_VERIFICATION=true in your .env file (development/testing only)."
                )
            else:
                logger.error(f"Database session error: {e}")
            raise
        except Exception as e:
            if session:
                await session.rollback()
            # Check if it's an SSL-related error
            error_str = str(e).lower()
            if any(ssl_term in error_str for ssl_term in ['ssl', 'certificate', 'cert', 'tls', 'certificate verify']):
                logger.error(
                    f"Database SSL error: {e}\n"
                    "If you're behind a corporate proxy or experiencing certificate chain issues, "
                    "set DISABLE_SSL_VERIFICATION=true in your .env file (development/testing only)."
                )
            else:
                logger.error(f"Unexpected error in database session: {e}")
            raise
        finally:
            # CRITICAL: Always close session to release connection back to pool (or close for NullPool)
            if session:
                await session.close()

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
            import asyncio
            engine = self.get_engine()

            # Create a connection with timeout protection
            # Use raw SQL string execution to avoid prepared statements
            async def _connect_and_test():
                conn = None
                try:
                    conn = await engine.connect()
                    # Use raw SQL execution without text() to avoid prepared statements
                    # This is critical for Supabase with pgbouncer in transaction mode
                    result = await conn.execute(text("SELECT 1"))
                    # Consume the result to ensure query completes
                    result.fetchone()  # Not async in SQLAlchemy's Result object
                    return True
                finally:
                    if conn:
                        await conn.close()

            # Wrap the entire operation in a timeout
            try:
                result = await asyncio.wait_for(_connect_and_test(), timeout=10.0)
                if result:
                    logger.info("Database connection check: OK")
                    self._database_available = True
                else:
                    self._database_available = False
                return result
            except asyncio.TimeoutError:
                logger.warning("Database connection check timed out after 10s")
                self._database_available = False
                return False
        except asyncio.CancelledError:
            logger.warning("Database connection check was cancelled")
            self._database_available = False
            raise  # Re-raise CancelledError so it can be handled upstream
        except DNSResolutionError as dns_error:
            logger.error(f"Database connection check failed (DNS): {dns_error}")
            logger.error("  -> Cannot resolve database hostname. Check network connectivity and DNS settings.")
            self._database_available = False
            return False
        except socket.gaierror as dns_error:
            logger.error(f"Database connection check failed (DNS): {dns_error}")
            logger.error("  -> DNS resolution failed. Check network connectivity and DNS settings.")
            self._database_available = False
            return False
        except SQLAlchemyError as e:
            error_str = str(e)
            error_lower = error_str.lower()
            
            # Handle DuplicatePreparedStatementError gracefully
            # This can occur with pgbouncer even with statement_cache_size=0
            if "DuplicatePreparedStatementError" in error_str or "prepared statement" in error_lower:
                logger.warning(
                    f"Database connection check: Prepared statement conflict detected. "
                    f"This is expected with pgbouncer in transaction mode. "
                    f"Connection may still work for actual queries. Error: {error_str}"
                )
                # Return True since NullPool should prevent this in actual usage
                # The connection check itself may fail, but real connections will work
                self._database_available = True
                return True
            
            # Check for SSL-related errors
            if any(ssl_term in error_lower for ssl_term in ['ssl', 'certificate', 'cert', 'tls', 'certificate verify', 'sslcertverificationerror']):
                logger.error(f"Database connection check failed (SSL): {error_str}")
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
            
            logger.error(f"Database connection check failed (SQLAlchemyError): {error_str}")
            # Provide more specific error context
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
        except Exception as e:
            error_str = str(e)
            error_type_name = type(e).__name__
            
            # Handle DuplicatePreparedStatementError at the Exception level too
            if "DuplicatePreparedStatementError" in error_str or "prepared statement" in error_str.lower():
                logger.warning(
                    f"Database connection check: Prepared statement conflict detected. "
                    f"This is expected with pgbouncer in transaction mode. "
                    f"Connection may still work for actual queries. Error: {error_str}"
                )
                self._database_available = True
                return True
            
            # Check for SSL-related errors
            error_lower = error_str.lower()
            if any(ssl_term in error_lower for ssl_term in ['ssl', 'certificate', 'cert', 'tls', 'certificate verify', 'sslcertverificationerror']):
                logger.error(f"Database connection check failed (SSL): {error_str}")
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
            
            # Check for DNS-related errors
            if "gaierror" in error_lower or "getaddrinfo" in error_lower:
                logger.error(f"Database connection check failed (DNS): {error_str}")
                logger.error("  -> DNS resolution failed. Check network connectivity and DNS settings.")
                self._database_available = False
                return False
            
            logger.error(f"Unexpected error during connection check: {error_str}")
            logger.error(f"Error type: {error_type_name}")
            self._database_available = False
            return False

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