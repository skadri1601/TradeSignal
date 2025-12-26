"""
TradeSignal API - Real-time insider trading intelligence platform.

FastAPI application with async database support, CORS, health checks,
comprehensive logging, and error handling.
"""

import sys
import asyncio
import os

# Fix for Windows asyncio loop with asyncpg/uvicorn
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv

load_dotenv()


import logging
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Any, Optional, Tuple

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import db_manager
from app.core.limiter import limiter
from app.core.observability import setup_observability
from app.middleware.error_handler import register_error_handlers
from app.services.cache_service import cache_service
from prometheus_fastapi_instrumentator import Instrumentator

# Background tasks registry
_background_tasks = set()

# Health check cache (to prevent connection pool exhaustion from frequent health checks)
_health_check_cache: Optional[Tuple[bool, datetime]] = None
_HEALTH_CHECK_CACHE_TTL = 15  # seconds


# Configure logging (Phase 5.4: Structured JSON logging in production)
if settings.is_production or os.getenv("USE_JSON_LOGGING", "false").lower() == "true":
    from app.core.logging_config import setup_json_logging

    setup_json_logging(level=settings.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Using structured JSON logging")
else:
    # Use human-readable logging in development
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)


# Configure rate limiter (uses in-memory storage, upgrade to Redis for production)
# limiter = Limiter(key_func=get_remote_address)  # Moved to app.core.limiter


async def background_db_reconnect():
    """
    Background task to periodically attempt database reconnection.

    Runs when database is initially unavailable. Attempts reconnection
    every 30 seconds until successful.
    """
    logger.info("🔄 Background database reconnection task started")
    attempt = 0

    while True:
        await asyncio.sleep(30)  # Wait 30 seconds between attempts

        # Check if database is already available
        if db_manager.is_available:
            logger.info("✅ Database is now available - stopping reconnection attempts")
            break

        attempt += 1
        logger.info(f"🔄 Attempting database reconnection (attempt #{attempt})...")

        try:
            connection_ok = await db_manager.check_connection()
            if connection_ok:
                logger.info(f"✅ Database reconnected successfully after {attempt} attempts")
                logger.info("📡 Application is now fully operational")
                break
            else:
                logger.warning(f"⚠️  Reconnection attempt #{attempt} failed - will retry in 30s")
        except Exception as e:
            logger.warning(f"⚠️  Reconnection attempt #{attempt} failed: {e} - will retry in 30s")


def _mask_database_url(db_url: str) -> str:
    """Mask password in database URL for logging."""
    masked_url = db_url
    try:
        if "@" in db_url and "://" in db_url:
            parts = db_url.split("://")
            if len(parts) == 2:
                protocol = parts[0]
                rest = parts[1]
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    if ":" in auth_part:
                        user, _ = auth_part.split(":", 1)
                        masked_url = f"{protocol}://{user}:***@{host_part}"
    except Exception:
        pass  # If masking fails, just use original
    return masked_url


def _format_db_error_messages(error_str: str, masked_url: str) -> None:
    """Format and log database error messages based on error type."""
    logger.error("=" * 80)
    logger.error(f" Database connection check FAILED: {error_str}")
    logger.error(" Possible causes:")
    
    error_lower = error_str.lower()
    if "gaierror" in error_lower or "getaddrinfo failed" in error_lower:
        logger.error("  - DNS resolution failed (cannot resolve database hostname)")
        logger.error("  - Check network connectivity and DNS settings")
        logger.error("  - Try flushing DNS cache: ipconfig /flushdns (Windows)")
        logger.error("  - Consider switching to Google DNS (8.8.8.8, 8.8.4.4)")
    elif "authentication" in error_lower or "password" in error_lower:
        logger.error("  - Incorrect username or password in DATABASE_URL")
    elif "does not exist" in error_lower or "database" in error_lower:
        logger.error("  - Database name does not exist")
    elif "could not connect" in error_lower or "connection refused" in error_lower:
        logger.error("  - Database server is not running or unreachable")
        logger.error("  - Check if host and port are correct")
    elif "timeout" in error_lower:
        logger.error("  - Connection timeout (network/firewall issue)")
    else:
        logger.error("  - Check DATABASE_URL format and credentials")
    
    logger.error(f" Database URL: {masked_url}")
    logger.error(" App will start but database operations will fail!")
    logger.error("=" * 80)


async def _check_database_connection(masked_url: str) -> bool:
    """Check database connection with timeout, retry logic, and error handling."""
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                logger.info(f" Retry attempt {attempt + 1}/{max_retries} - Testing database connection...")
            else:
                logger.info(" Testing database connection...")

            db_connected = await asyncio.wait_for(
                db_manager.check_connection(),
                timeout=25.0  # 25 second timeout per attempt (less than database.py's 30s timeout)
            )

            if db_connected:
                if attempt > 0:
                    logger.info(f"✅ Database connection established on attempt {attempt + 1}/{max_retries}")
                return True
            else:
                if attempt < max_retries - 1:
                    logger.warning(f" Database connection attempt {attempt + 1}/{max_retries} failed, retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(" Database connection failed after all retry attempts")
                    return False

        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                logger.warning(f" Database connection TIMED OUT on attempt {attempt + 1}/{max_retries}, retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("=" * 80)
                logger.error(f" Database connection check TIMED OUT after {max_retries} attempts")
                logger.error(" Possible causes:")
                logger.error("  1. Database server is not running or unreachable")
                logger.error("  2. Network/firewall blocking connection")
                logger.error("  3. Incorrect DATABASE_URL (wrong host/port)")
                logger.error("  4. Database server is overloaded")
                logger.error(f" Database URL: {masked_url}")
                logger.error(" App will start but database operations will fail!")
                logger.error("=" * 80)
                return False

        except asyncio.CancelledError:
            logger.warning(" Database connection check was cancelled")
            raise  # Re-raise to allow proper cancellation propagation

        except Exception as db_error:
            if attempt < max_retries - 1:
                logger.warning(f" Database connection error on attempt {attempt + 1}/{max_retries}: {db_error}, retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                _format_db_error_messages(str(db_error), masked_url)
                return False

    return False


async def _create_database_tables() -> None:
    """Create database tables if they don't exist."""
    try:
        from app.database import Base
        from app.models import ScrapeJob, ScrapeHistory, ContactSubmission  # noqa: F401

        async def _create_tables():
            engine = db_manager.get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        try:
            await asyncio.wait_for(_create_tables(), timeout=30.0)
            logger.info("✅ Database tables created/verified")
        except asyncio.TimeoutError:
            logger.warning("⚠️  Database table creation timed out (tables may already exist)")
    except Exception as e:
        logger.warning(f"⚠️  Failed to create tables: {e}")


def _log_startup_info(app: FastAPI) -> None:
    """Log startup information including routes and feature flags."""
    logger.info("Application startup complete")
    logger.info("=" * 80)
    
    # Log feature flags
    logger.info(
        f"AI Insights: {'Enabled' if settings.enable_ai_insights else 'Disabled'}"
    )
    logger.info(
        f"Webhooks: {'Enabled' if settings.enable_webhooks else 'Disabled'}"
    )
    logger.info(
        f"Email Alerts: {'Enabled' if settings.enable_email_alerts else 'Disabled'}"
    )
    logger.info(
        f"Push Notifications: {'Enabled' if settings.enable_push_notifications else 'Disabled'}"
    )
    
    # Log all registered routes for debugging
    logger.info("Registered Routes:")
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            logger.info(f" - {route.path} [{','.join(route.methods)}]")
        elif hasattr(route, "path"):
            # WebSocket routes don't have methods
            logger.info(f" - {route.path} [WebSocket]")
    
    logger.info("=" * 80)
    logger.info("Server is ready to accept connections")
    logger.info(f"API available at: http://0.0.0.0:8000{settings.api_v1_prefix}/docs")


async def _shutdown_application() -> None:
    """Handle application shutdown sequence."""
    logger.info("Shutting down application...")

    # Cancel background tasks
    logger.info(f"Cancelling {len(_background_tasks)} background tasks...")
    for task in _background_tasks:
        task.cancel()
    # Wait for all background tasks to finish cancellation
    if _background_tasks:
        await asyncio.gather(*_background_tasks, return_exceptions=True)
        logger.info("Background tasks cancelled")

    # Close database connections (with shorter timeout and force close)
    try:
        try:
            await asyncio.wait_for(db_manager.close(), timeout=2.0)
            logger.info(" Database connections closed")
        except asyncio.TimeoutError:
            logger.warning(" Database close timed out, forcing close")
            # Force close by setting engine to None
            if db_manager._engine is not None:
                db_manager._engine = None
                db_manager._session_factory = None
                logger.info(" Database engine force-closed")
        except asyncio.CancelledError:
            logger.warning(" Database close was cancelled")
            raise  # Re-raise to allow proper cancellation propagation
    except asyncio.CancelledError:
        # Re-raise CancelledError to allow proper cancellation propagation
        raise
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")
        # Force close on any error
        if db_manager._engine is not None:
            db_manager._engine = None
            db_manager._session_factory = None

    # Disconnect cache service
    try:
        await cache_service.disconnect()
        logger.info("Cache service disconnected")
    except Exception as e:
        logger.warning(f"Cache service disconnect error: {e}")

    logger.info("Application shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database connection, log configuration
    - Shutdown: Close database connections, cleanup resources
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"Starting {settings.project_name} v{settings.project_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info("=" * 80)

    # Track if we're setting up degraded mode due to cancellation
    degraded_mode_due_to_cancellation = False
    
    try:
        # Check if DATABASE_URL is configured
        db_url = settings.database_url
        if not db_url or db_url.strip() == "":
            logger.error("=" * 80)
            logger.error(" CRITICAL: DATABASE_URL is not set or is empty!")
            logger.error(" Please set DATABASE_URL in your .env file or environment variables")
            logger.error(" Example: DATABASE_URL=postgresql://user:password@host:port/database")
            logger.error("=" * 80)
            db_connected = False
        else:
            masked_url = _mask_database_url(db_url)
            logger.info(f" Database URL configured: {masked_url}")
            try:
                db_connected = await _check_database_connection(masked_url)
            except asyncio.CancelledError as cancel_error:
                # If connection check is cancelled, log and set degraded mode
                # Re-raise after cleanup to allow proper cancellation propagation
                logger.warning(" Database connection check was cancelled - starting in degraded mode")
                db_connected = False
                degraded_mode_due_to_cancellation = True
                # Re-raise to allow proper cancellation propagation
                raise cancel_error

        if db_connected:
            logger.info("✅ Database connection established")
            await _create_database_tables()
        else:
            logger.warning("=" * 80)
            logger.warning("⚠️  DATABASE UNAVAILABLE - Starting in degraded mode")
            logger.warning("⚠️  Endpoints requiring database will return 503 SERVICE UNAVAILABLE")
            logger.warning("⚠️  Background reconnection task will attempt to restore connectivity")
            logger.warning("=" * 80)

            # Start background reconnection task
            task = asyncio.create_task(background_db_reconnect())
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)
            logger.info("🔄 Background database reconnection task started")

        _log_startup_info(app)

    except asyncio.CancelledError as cancel_error:
        # If cancellation occurred during connection check and we set up degraded mode,
        # allow startup to continue in degraded mode
        # Otherwise, re-raise to allow proper cancellation propagation
        if degraded_mode_due_to_cancellation:
            logger.info(" Continuing startup in degraded mode despite connection check cancellation")
            # Suppress cancellation to allow degraded mode startup
            # This is intentional - we want the app to start even if connection check is cancelled
        else:
            # Re-raise CancelledError to allow proper cancellation propagation
            raise cancel_error
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise

    # Yield control to FastAPI - server starts here
    yield
    
    # This point is reached during shutdown
    logger.info("Lifespan yield returned - starting shutdown sequence")
    await _shutdown_application()


# Initialize FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="Real-time insider trading intelligence platform. Track SEC Form 4 filings, "
    "congressional trades, and get AI-powered insights on market-moving transactions.",
    version=settings.project_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Prometheus metrics: instrument the FastAPI app and expose /metrics
try:
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus instrumentator registered (/metrics)")
except Exception as e:
    logger.warning(f"Prometheus instrumentation failed to initialize: {e}")

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register error handlers
register_error_handlers(app)


# CORS Middleware Configuration (must be added before HTTPS redirect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Explicit whitelist
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],  # Explicit whitelist
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=600,  # Cache preflight for 10 minutes
)

# HTTPS Redirect and Security Headers Middleware
from app.middleware.https_redirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests with method, path, status, and duration.

    Provides visibility into API usage and performance.
    Enhanced with error handling and detailed logging.
    """
    start_time = time.time()
    request_id = id(request)  # Simple request identifier

    # Log request start
    logger.debug(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    try:
        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log request details
        log_level = logger.warning if response.status_code >= 400 else logger.info
        log_level(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration_ms}ms"
        )

        # Log slow requests
        if duration > 1.0:
            logger.warning(
                f"[{request_id}] Slow request detected: {request.method} {request.url.path} - "
                f"Duration: {duration_ms}ms"
            )

        # Log error responses
        if response.status_code >= 500:
            logger.error(
                f"[{request_id}] Server error: {request.method} {request.url.path} - "
                f"Status: {response.status_code}"
            )

        return response
    except Exception as e:
        # Calculate duration even on error
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log the error
        logger.error(
            f"[{request_id}] Request failed: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Duration: {duration_ms}ms",
            exc_info=True,
        )

        # Re-raise to let exception handlers deal with it
        raise


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent JSON response format.

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} - "
        f"Path: {request.method} {request.url.path}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors with detailed error messages.

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(
        f"Validation Error: {request.method} {request.url.path} - "
        f"Errors: {exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all uncaught exceptions with generic error response.

    Prevents sensitive error details from leaking in production.
    Ensures all exceptions return proper JSON responses (never empty).

    Returns:
        JSONResponse with generic error message
    """
    # Log the full exception with stack trace
    logger.error(
        f"Unhandled Exception: {request.method} {request.url.path} - "
        f"Error Type: {type(exc).__name__} - "
        f"Error: {str(exc)}",
        exc_info=True,
    )

    # Show detailed error only in development
    error_detail = str(exc) if settings.debug else "Internal Server Error"

    # Ensure we always return a proper JSON response, never empty
    try:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": error_detail,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": str(request.url.path),
            },
        )
    except Exception as response_error:
        # Even if JSONResponse fails, log and return a basic response
        logger.critical(
            f"Failed to create error response: {response_error}", exc_info=True
        )
        # Return a minimal response
        from fastapi.responses import Response

        return Response(
            content='{"error":"Internal Server Error"}',
            status_code=500,
            media_type="application/json",
        )


# Root Endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """
    Welcome endpoint with API information.

    Returns:
        dict: API welcome message and documentation links
    """
    return {
        "message": "Welcome to TradeSignal API",
        "description": "Real-time insider trading intelligence platform",
        "version": settings.project_version,
        "environment": settings.environment,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json",
        },
        "features": {
            "ai_insights": settings.enable_ai_insights,
            "webhooks": settings.enable_webhooks,
            "email_alerts": settings.enable_email_alerts,
            "push_notifications": settings.enable_push_notifications,
        },
    }


# Health Check Endpoint (with caching to prevent connection pool exhaustion)
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.

    Implements 15-second caching to prevent connection pool exhaustion from
    frequent health checks (Render checks every ~5 seconds).

    Checks:
        - API availability
        - Database connectivity (cached for 15s)
        - Timestamp for request tracking

    Returns:
        dict: Health status with database connectivity and timestamp

    Status Codes:
        - 200: Healthy (API and database both OK)
        - 503: Unhealthy (database connection failed)
    """
    global _health_check_cache

    try:
        # Check if we have a valid cached result
        now = datetime.now(timezone.utc)
        if _health_check_cache is not None:
            cached_result, cached_time = _health_check_cache
            cache_age = (now - cached_time).total_seconds()

            if cache_age < _HEALTH_CHECK_CACHE_TTL:
                # Return cached result
                response = {
                    "status": "healthy" if cached_result else "unhealthy",
                    "timestamp": now.isoformat(),
                    "version": settings.project_version,
                    "environment": settings.environment,
                    "checks": {
                        "api": "ok",
                        "database": "ok" if cached_result else "error",
                    },
                    "cache": {
                        "hit": True,
                        "age_seconds": round(cache_age, 1)
                    }
                }

                if not cached_result:
                    return JSONResponse(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        content=response,
                    )
                return response

        # Cache miss or expired - perform actual database check
        try:
            # Add timeout at endpoint level (25s, less than database.py's 30s timeout)
            db_healthy = await asyncio.wait_for(
                db_manager.check_connection(),
                timeout=25.0
            )
        except asyncio.TimeoutError:
            logger.warning("Health check: Database connection check timed out after 25s")
            db_healthy = False
        except Exception as db_error:
            logger.error(
                f"Health check: Database connection check failed: {db_error}",
                exc_info=True,
            )
            db_healthy = False

        # Update cache with result
        _health_check_cache = (db_healthy, now)

        response = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": now.isoformat(),
            "version": settings.project_version,
            "environment": settings.environment,
            "checks": {
                "api": "ok",
                "database": "ok" if db_healthy else "error",
            },
            "cache": {
                "hit": False,
                "age_seconds": 0
            }
        }

        # Return 503 if unhealthy
        if not db_healthy:
            logger.warning("Health check failed: Database connection error")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=response,
            )

        return response
    except Exception as e:
        # Even if health check itself fails, return a response
        logger.critical(f"Health check endpoint failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": settings.project_version,
                "environment": settings.environment,
                "checks": {
                    "api": "error",
                    "database": "unknown",
                },
                "error": "Health check failed",
            },
        )


# API v1 Routers (imported here to avoid circular dependencies)
from app.routers import (  # noqa: E402
    auth,
    trades,
    companies,
    insiders,
    scraper,
    scheduler,
    push,
    stocks,
    health,
    congressional_trades,
    congresspeople,
    billing,
    fed,
    orders,
    admin,
    contact,
    jobs,
    news,
    public_contact,
    data_health,
    notifications,
    ai,
    # REMOVED: patterns (file was deleted by Gemini along with pattern_analysis_service)
    alerts,
    research,
    forum,
    brokerage,
)
from app.routers import enterprise_api  # noqa: E402

# Include all routers with API v1 prefix
app.include_router(
    auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"]
)
app.include_router(
    trades.router, prefix=f"{settings.api_v1_prefix}/trades", tags=["Trades"]
)
app.include_router(
    companies.router, prefix=f"{settings.api_v1_prefix}/companies", tags=["Companies"]
)
app.include_router(
    insiders.router, prefix=f"{settings.api_v1_prefix}/insiders", tags=["Insiders"]
)
app.include_router(
    scraper.router, prefix=f"{settings.api_v1_prefix}/scraper", tags=["Scraper"]
)
app.include_router(
    scheduler.router, prefix=f"{settings.api_v1_prefix}/scheduler", tags=["Scheduler"]
)
app.include_router(
    push.router, prefix=f"{settings.api_v1_prefix}", tags=["Push Notifications"]
)
app.include_router(
    stocks.router, prefix=f"{settings.api_v1_prefix}", tags=["Stock Prices"]
)
# COMMENTED OUT: Duplicate health router conflicts with main app health check at GET /health
# app.include_router(
#     health.router, prefix=f"{settings.api_v1_prefix}", tags=["Health Checks"]
# )
app.include_router(
    data_health.router, prefix=f"{settings.api_v1_prefix}/data-health", tags=["Data Health Checks"]
)
app.include_router(
    notifications.router, prefix=f"{settings.api_v1_prefix}/notifications", tags=["Notifications"]
)
app.include_router(
    ai.router, prefix=f"{settings.api_v1_prefix}", tags=["AI Insights"]
)
# REMOVED: patterns router (file was deleted by Gemini along with pattern_analysis_service)
# app.include_router(
#     patterns.router, prefix=f"{settings.api_v1_prefix}", tags=["Pattern Analysis"]
# )
app.include_router(
    congressional_trades.router,
    prefix=f"{settings.api_v1_prefix}/congressional-trades",
    tags=["Congressional Trades"],
)
app.include_router(
    congresspeople.router,
    prefix=f"{settings.api_v1_prefix}/congresspeople",
    tags=["Congresspeople"],
)
app.include_router(billing.router, prefix=f"{settings.api_v1_prefix}", tags=["Billing"])
app.include_router(
    fed.router, prefix=f"{settings.api_v1_prefix}", tags=["Federal Reserve"]
)
app.include_router(
    orders.router, prefix=f"{settings.api_v1_prefix}/billing", tags=["Orders"]
)
app.include_router(
    admin.router, prefix=f"{settings.api_v1_prefix}/admin", tags=["Admin"]
)
app.include_router(contact.router, prefix=f"{settings.api_v1_prefix}", tags=["Contact"])
app.include_router(public_contact.router, prefix=f"{settings.api_v1_prefix}", tags=["Public Contact"])
app.include_router(jobs.router, prefix=f"{settings.api_v1_prefix}", tags=["Jobs"])
app.include_router(news.router, prefix=f"{settings.api_v1_prefix}", tags=["News"])
from app.routers import tickets  # noqa: E402

app.include_router(tickets.router, prefix=f"{settings.api_v1_prefix}", tags=["Tickets"])
app.include_router(alerts.router, prefix=f"{settings.api_v1_prefix}", tags=["Alerts"])
app.include_router(research.router, tags=["Research"])  # Research router has its own /api/research prefix
app.include_router(
    forum.router, prefix=f"{settings.api_v1_prefix}/forum", tags=["Forum"]
)
app.include_router(
    brokerage.router, prefix=f"{settings.api_v1_prefix}/brokerage", tags=["Brokerage"]
)
app.include_router(
    enterprise_api.router, prefix=f"{settings.api_v1_prefix}", tags=["Enterprise API"]
)
from app.routers import api_docs, enterprise_research_api, marketing_api, webhook_api, visualization_api, pricing_api, health_api  # noqa: E402

app.include_router(
    api_docs.router, prefix=f"{settings.api_v1_prefix}", tags=["API Documentation"]
)
app.include_router(
    enterprise_research_api.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Enterprise Research API"],
)
app.include_router(
    marketing_api.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Marketing"],
)
app.include_router(
    webhook_api.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Webhooks"],
)
app.include_router(
    visualization_api.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Visualizations"],
)
app.include_router(
    pricing_api.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Pricing"],
)
# COMMENTED OUT: Duplicate health_api router conflicts with main app health check at GET /health
# app.include_router(
#     health_api.router,
#     prefix=f"{settings.api_v1_prefix}",
#     tags=["Health"],
# )


if __name__ == "__main__":
    import uvicorn
    import uvicorn.logging

    # Configure uvicorn logging to use our logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(getattr(logging, settings.log_level))
    
    # Run with uvicorn when executed directly
    # For production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000
    logger.info("=" * 80)
    logger.info("Starting Uvicorn server...")
    logger.info("Host: 0.0.0.0, Port: 8000")
    logger.info(f"Reload: {settings.debug}")
    logger.info(f"Log Level: {settings.log_level.lower()}")
    logger.info("=" * 80)
    
    try:
        # Use app object directly to avoid any import delays or issues
        # This ensures the app is fully loaded before uvicorn starts
        uvicorn.run(
            app,  # Pass app object directly
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload when passing app object (reload requires string)
            log_level=settings.log_level.lower(),
            timeout_keep_alive=5,
            timeout_graceful_shutdown=5,  # Reduced from 10 to 5 seconds
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user (Ctrl+C)")
        # FastAPI's lifespan will handle cleanup
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
