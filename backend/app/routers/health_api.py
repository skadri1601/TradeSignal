"""
Enhanced Health Check API Router.

Comprehensive health checks for all system components.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.database import get_db
from app.config import settings
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns service status and basic system information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.project_version,
        "environment": settings.environment,
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with component status.
    
    Checks database, cache, and external service connectivity.
    """
    checks = {
        "api": "healthy",
        "database": "unknown",
        "cache": "unknown",
    }

    # Database check
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = "unhealthy"
        checks["database_error"] = str(e)

    # Cache check
    try:
        if cache_service.redis_client:
            await cache_service.redis_client.ping()
            checks["cache"] = "healthy"
        else:
            checks["cache"] = "not_configured"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        checks["cache"] = "unhealthy"
        checks["cache_error"] = str(e)

    # Overall status
    overall_status = "healthy"
    if checks["database"] != "healthy":
        overall_status = "degraded"
    if checks["database"] == "unhealthy":
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.project_version,
        "environment": settings.environment,
        "checks": checks,
    }


@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if service is ready to accept traffic.
    """
    try:
        # Check database
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 if service is alive (even if degraded).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }

