"""
Health Check Endpoints for TradeSignal.

Provides health status endpoints for monitoring and uptime checks.
Based on TRUTH_FREE.md Phase 5.3.
"""

from fastapi import APIRouter, status as http_status
from datetime import datetime
import os
import logging
from typing import Dict, Any

from app.database import db_manager
from app.core.redis_cache import get_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def basic_health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns basic application status.
    Used by load balancers and simple monitoring tools.

    Returns:
        dict: Health status with timestamp and version
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": os.getenv("GIT_COMMIT_SHA", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@router.get("/detailed")
async def detailed_health_check() -> tuple[Dict[str, Any], int]:
    """
    Detailed health check with dependency status.

    Checks all critical services:
    - Database connectivity
    - Redis cache
    - Data sources (Yahoo Finance, Finnhub, Alpha Vantage)

    Returns:
        tuple: (health_data, status_code)
            - 200 if all services healthy
            - 503 if any service degraded/unhealthy
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": os.getenv("GIT_COMMIT_SHA", "unknown"),
        "services": {}
    }

    # Check database
    try:
        db_healthy = await db_manager.check_connection()
        if db_healthy:
            health["services"]["database"] = {
                "status": "healthy",
                "message": "PostgreSQL connection OK"
            }
        else:
            health["services"]["database"] = {
                "status": "unhealthy",
                "message": "PostgreSQL connection failed"
            }
            health["status"] = "degraded"
    except Exception as e:
        health["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        cache = get_cache()
        if cache and cache.enabled():
            # Try a simple operation
            test_key = "health:check"
            cache.set(test_key, {"test": "ok"}, ttl=10)
            result = cache.get(test_key)

            if result and result.get("test") == "ok":
                health["services"]["redis"] = {
                    "status": "healthy",
                    "message": "Redis connection OK"
                }
            else:
                health["services"]["redis"] = {
                    "status": "degraded",
                    "message": "Redis responding but data inconsistent"
                }
                health["status"] = "degraded"
        else:
            health["services"]["redis"] = {
                "status": "unavailable",
                "message": "Redis not configured or disabled (using in-memory fallback)"
            }
            # Not critical - we have fallback
    except Exception as e:
        health["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")

    # Check data sources (import here to avoid circular dependencies)
    try:
        from app.services.stock_price_service import (
            _yahoo_consecutive_failures,
            _finnhub_consecutive_failures,
            _alpha_vantage_consecutive_failures
        )

        health["services"]["data_sources"] = {
            "yahoo_finance": {
                "status": "healthy" if _yahoo_consecutive_failures < 3 else "unhealthy",
                "consecutive_failures": _yahoo_consecutive_failures
            },
            "finnhub": {
                "status": "healthy" if _finnhub_consecutive_failures < 3 else "unhealthy",
                "consecutive_failures": _finnhub_consecutive_failures
            },
            "alpha_vantage": {
                "status": "healthy" if _alpha_vantage_consecutive_failures < 3 else "unhealthy",
                "consecutive_failures": _alpha_vantage_consecutive_failures
            }
        }

        # If primary source (Yahoo) is down, mark as degraded
        if _yahoo_consecutive_failures >= 3:
            health["status"] = "degraded"

    except Exception as e:
        health["services"]["data_sources"] = {
            "status": "unknown",
            "error": str(e)
        }
        logger.error(f"Data sources health check failed: {e}")

    # Determine HTTP status code
    status_code = (
        http_status.HTTP_200_OK
        if health["status"] == "healthy"
        else http_status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return health, status_code


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe.

    Checks if the application is ready to serve traffic.
    Used by Kubernetes/Docker orchestration.

    Returns:
        dict: Readiness status
    """
    try:
        # Check if database is accessible
        db_healthy = await db_manager.check_connection()

        if db_healthy:
            return {
                "ready": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "ready": False,
                "reason": "Database not accessible",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes-style liveness probe.

    Checks if the application is alive and responding.
    Used by Kubernetes to detect if container needs restart.

    Returns:
        dict: Liveness status (always returns 200 if app is running)
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }
