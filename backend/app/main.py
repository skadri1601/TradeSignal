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
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import db_manager
from prometheus_fastapi_instrumentator import Instrumentator

# Sentry error tracking
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if settings.is_production and os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=settings.environment,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        send_default_pii=False,  # Don't send personally identifiable information
    )
    logging.info("Sentry error tracking initialized")
elif os.getenv("SENTRY_DSN"):
    # Development mode with Sentry
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment="development",
        traces_sample_rate=1.0,  # 100% tracing in dev
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
    )
    logging.info("Sentry error tracking initialized (development mode)")



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
limiter = Limiter(key_func=get_remote_address)


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
        # Test database connection
        db_connected = await db_manager.check_connection()
        if db_connected:
            logger.info(" Database connection established")

            # Create database tables (if they don't exist)
            try:
                from app.database import Base
                from app.models import ScrapeJob, ScrapeHistory  # Import to register with metadata

                engine = db_manager.get_engine()
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info(" Database tables created/verified")
            except Exception as e:
                logger.warning(f" Failed to create tables: {e}")
        else:
            logger.warning(" Database connection failed (app will start anyway)")

        # Log feature flags
        logger.info(f"AI Insights: {'Enabled' if settings.enable_ai_insights else 'Disabled'}")
        logger.info(f"Webhooks: {'Enabled' if settings.enable_webhooks else 'Disabled'}")
        logger.info(f"Email Alerts: {'Enabled' if settings.enable_email_alerts else 'Disabled'}")
        logger.info(f"Push Notifications: {'Enabled' if settings.enable_push_notifications else 'Disabled'}")

        # Start scheduler if enabled
        if settings.scheduler_enabled:
            from app.services.scheduler_service import scheduler_service
            await scheduler_service.start()
            logger.info(" Scheduler started - automated scraping enabled")
        else:
            logger.info(" Scheduler disabled (SCHEDULER_ENABLED=false)")

        logger.info("Application startup complete")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        await db_manager.close()
        logger.info(" Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
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
from app.middleware import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)

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
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time
    duration_ms = round(duration * 1000, 2)

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration_ms}ms"
    )

    return response


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

    Returns:
        JSONResponse with generic error message
    """
    logger.error(
        f"Unhandled Exception: {request.method} {request.url.path} - "
        f"Error: {str(exc)}",
        exc_info=True,
    )

    # Show detailed error only in development
    error_detail = str(exc) if settings.debug else "Internal Server Error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": error_detail,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        },
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
async def health_check() -> dict[str, Any] | JSONResponse:
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
    # Check database connectivity
    db_healthy = await db_manager.check_connection()

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


# API v1 Routers
from app.routers import trades, companies, insiders, scraper, scheduler, alerts, push, ai, stocks, health, tasks, billing

# Include all routers with API v1 prefix
app.include_router(
    trades.router,
    prefix=f"{settings.api_v1_prefix}/trades",
    tags=["Trades"]
)
app.include_router(
    companies.router,
    prefix=f"{settings.api_v1_prefix}/companies",
    tags=["Companies"]
)
app.include_router(
    insiders.router,
    prefix=f"{settings.api_v1_prefix}/insiders",
    tags=["Insiders"]
)
app.include_router(
    scraper.router,
    prefix=f"{settings.api_v1_prefix}/scraper",
    tags=["Scraper"]
)
app.include_router(
    alerts.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Alerts"]
)
app.include_router(
    scheduler.router,
    prefix=f"{settings.api_v1_prefix}/scheduler",
    tags=["Scheduler"]
)
app.include_router(
    push.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Push Notifications"]
)
app.include_router(
    ai.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["AI Insights"]
)
app.include_router(
    stocks.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Stock Prices"]
)
app.include_router(
    health.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Health Checks"]
)
app.include_router(
    tasks.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Background Tasks"]
)
app.include_router(
    billing.router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["Billing"]
)


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn when executed directly
    # For production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
