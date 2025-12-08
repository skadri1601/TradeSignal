"""
TradeSignal API - Real-time insider trading intelligence platform.

FastAPI application with async database support, CORS, health checks,
comprehensive logging, and error handling.
"""

from dotenv import load_dotenv

load_dotenv()


import logging
import time
import os
import signal
import sys
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any

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
from prometheus_fastapi_instrumentator import Instrumentator


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

    try:
        # Test database connection with timeout and error handling
        db_connected = False
        try:
            import asyncio
            # Add shorter timeout to prevent hanging on connection (5 seconds)
            # Use asyncio.wait_for with a task to ensure it can be cancelled
            db_connected = await asyncio.wait_for(
                db_manager.check_connection(),
                timeout=5.0  # 5 second timeout - reduced from 10 to fail faster
            )
        except asyncio.TimeoutError:
            logger.warning(" Database connection check timed out after 5s (app will start anyway)")
            db_connected = False
        except asyncio.CancelledError:
            logger.warning(" Database connection check was cancelled (app will start anyway)")
            db_connected = False
        except Exception as db_error:
            logger.warning(f" Database connection check failed: {db_error} (app will start anyway)")
            db_connected = False

        if db_connected:
            logger.info(" Database connection established")

            # Create database tables (if they don't exist) with timeout
            try:
                import asyncio
                from app.database import Base

                # Import models to register with metadata
                from app.models import ScrapeJob, ScrapeHistory, ContactSubmission  # noqa: F401

                async def _create_tables():
                engine = db_manager.get_engine()
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
                # Add timeout to table creation to prevent hanging
                try:
                    await asyncio.wait_for(_create_tables(), timeout=10.0)
                logger.info(" Database tables created/verified")
                except asyncio.TimeoutError:
                    logger.warning(" Database table creation timed out (tables may already exist)")
            except Exception as e:
                logger.warning(f" Failed to create tables: {e}")
        else:
            logger.warning(" Database connection failed (app will start anyway)")

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

        # Start scheduler if enabled
        if settings.scheduler_enabled:
            from app.services.scheduler_service import scheduler_service

            await scheduler_service.start()
            logger.info(" Scheduler started - automated scraping enabled")
            logger.info(f" Scheduled scraping hours: {settings.scraper_schedule_hours}")
            logger.info(f" Scraper timezone: {settings.scraper_timezone}")
            logger.info(
                f" Days back: {settings.scraper_days_back}, Max filings: {settings.scraper_max_filings}"
            )
            jobs = scheduler_service.get_jobs()
            logger.info(f" Active scheduled jobs: {len(jobs)}")
            for job in jobs:
                logger.info(
                    f"  - {job.name} (ID: {job.id}, Next run: {job.next_run_time})"
                )
        else:
            logger.info(" Scheduler disabled (SCHEDULER_ENABLED=false)")

        logger.info("Application startup complete")
        logger.info("=" * 80)
        logger.info("Server is ready to accept connections")
        logger.info(f"API available at: http://0.0.0.0:8000{settings.api_v1_prefix}/docs")

    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise

    # Yield control to FastAPI - server starts here
    yield
    
    # This point is reached during shutdown
    logger.info("Lifespan yield returned - starting shutdown sequence")

    # Shutdown
    logger.info("Shutting down application...")
    try:
        # Stop scheduler first (with timeout to prevent hanging)
        if settings.scheduler_enabled:
            try:
                from app.services.scheduler_service import scheduler_service
                import asyncio
                # Stop scheduler with timeout
                await asyncio.wait_for(scheduler_service.stop(), timeout=5.0)
                logger.info(" Scheduler stopped")
            except asyncio.TimeoutError:
                logger.warning(" Scheduler stop timed out, forcing shutdown")
            except Exception as e:
                logger.error(f" Error stopping scheduler: {e}")
    except Exception as e:
        logger.error(f"Error during scheduler shutdown: {e}")
    
    try:
        # Close database connections (with timeout)
        import asyncio
        await asyncio.wait_for(db_manager.close(), timeout=5.0)
        logger.info(" Database connections closed")
    except asyncio.TimeoutError:
        logger.warning(" Database close timed out")
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")
    
    logger.info("Application shutdown complete")


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


# HTTPS Redirect and Security Headers Middleware (must be added first)
# Commented out - middleware not yet implemented
# from app.middleware import HTTPSRedirectMiddleware
# app.add_middleware(HTTPSRedirectMiddleware)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


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
            "timestamp": datetime.utcnow().isoformat(),
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
            "timestamp": datetime.utcnow().isoformat(),
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
                "timestamp": datetime.utcnow().isoformat(),
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


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.

    Checks:
        - API availability
        - Database connectivity
        - Timestamp for request tracking

    Returns:
        dict: Health status with database connectivity and timestamp

    Status Codes:
        - 200: Healthy (API and database both OK)
        - 503: Unhealthy (database connection failed)
    """
    try:
        # Check database connectivity with error handling
        try:
            db_healthy = await db_manager.check_connection()
        except Exception as db_error:
            logger.error(
                f"Health check: Database connection check failed: {db_error}",
                exc_info=True,
            )
            db_healthy = False

        # Overall health status
        is_healthy = db_healthy

        response = {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.project_version,
            "environment": settings.environment,
            "checks": {
                "api": "ok",
                "database": "ok" if db_healthy else "error",
            },
        }

        # Return 503 if unhealthy
        if not is_healthy:
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
                "timestamp": datetime.utcnow().isoformat(),
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
)

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
app.include_router(
    health.router, prefix=f"{settings.api_v1_prefix}", tags=["Health Checks"]
)
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


if __name__ == "__main__":
    import uvicorn
    import uvicorn.logging

    # Configure uvicorn logging to use our logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(getattr(logging, settings.log_level))
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        """Handle SIGINT (Ctrl+C) and SIGTERM for graceful shutdown."""
        logger.info("\nReceived shutdown signal, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run with uvicorn when executed directly
    # For production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000
    logger.info("=" * 80)
    logger.info("Starting Uvicorn server...")
    logger.info(f"Host: 0.0.0.0, Port: 8000")
    logger.info(f"Reload: {settings.debug}")
    logger.info(f"Log Level: {settings.log_level.lower()}")
    logger.info("=" * 80)
    logger.info("Calling uvicorn.run() - server should start now...")
    
    try:
        # Use log_config to ensure proper logging
        logger.info("Initializing uvicorn server...")
        logger.info("About to call uvicorn.run() - this will start the server")
        
        # Use app object directly to avoid any import delays or issues
        # This ensures the app is fully loaded before uvicorn starts
        uvicorn.run(
            app,  # Pass app object directly
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload when passing app object (reload requires string)
            log_level=settings.log_level.lower(),
            timeout_keep_alive=5,
            timeout_graceful_shutdown=10,
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)
