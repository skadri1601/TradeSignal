"""
Health Check Endpoints for TradeSignal.

Provides health status endpoints for monitoring and uptime checks.
Based on TRUTH_FREE.md Phase 5.3.
"""

from fastapi import APIRouter, status as http_status
from datetime import datetime
import os
import logging
import asyncio
from typing import Dict, Any

from app.database import db_manager
from app.config import settings

# NOTE: Redis cache removed - caching now uses Supabase

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
        "environment": os.getenv("ENVIRONMENT", "development"),
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
        "services": {},
    }

    # Check database
    try:
        db_healthy = await db_manager.check_connection()
        if db_healthy:
            health["services"]["database"] = {
                "status": "healthy",
                "message": "PostgreSQL connection OK",
            }
        else:
            health["services"]["database"] = {
                "status": "unhealthy",
                "message": "PostgreSQL connection failed",
            }
            health["status"] = "degraded"
    except Exception as e:
        health["services"]["database"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Redis has been removed - now using Supabase caching
    health["services"]["cache"] = {
        "status": "disabled",
        "message": "Redis removed - using Supabase caching instead",
    }

    # Check data sources (import here to avoid circular dependencies)
    try:
        from app.services.stock_price_service import (
            _yahoo_consecutive_failures,
            _finnhub_consecutive_failures,
            _alpha_vantage_consecutive_failures,
        )

        health["services"]["data_sources"] = {
            "yahoo_finance": {
                "status": "healthy" if _yahoo_consecutive_failures < 3 else "unhealthy",
                "consecutive_failures": _yahoo_consecutive_failures,
            },
            "finnhub": {
                "status": "healthy"
                if _finnhub_consecutive_failures < 3
                else "unhealthy",
                "consecutive_failures": _finnhub_consecutive_failures,
            },
            "alpha_vantage": {
                "status": "healthy"
                if _alpha_vantage_consecutive_failures < 3
                else "unhealthy",
                "consecutive_failures": _alpha_vantage_consecutive_failures,
            },
        }

        # If primary source (Yahoo) is down, mark as degraded
        if _yahoo_consecutive_failures >= 3:
            health["status"] = "degraded"

    except Exception as e:
        health["services"]["data_sources"] = {"status": "unknown", "error": str(e)}
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
            return {"ready": True, "timestamp": datetime.now().isoformat()}
        else:
            return {
                "ready": False,
                "reason": "Database not accessible",
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "reason": str(e),
            "timestamp": datetime.now().isoformat(),
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
    return {"alive": True, "timestamp": datetime.now().isoformat()}


@router.get("/database-diagnostics")
async def database_diagnostics() -> Dict[str, Any]:
    """
    Database diagnostic endpoint for troubleshooting connection issues.
    
    Provides detailed information about database configuration and connection status.
    Useful for debugging connection problems.
    
    Returns:
        dict: Diagnostic information (passwords are masked)
    """
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "database_configured": False,
        "connection_status": "unknown",
        "connection_test": None,
        "configuration": {},
        "recommendations": [],
    }
    
    # Check if DATABASE_URL is set
    db_url = settings.database_url if hasattr(settings, 'database_url') else None
    
    if not db_url or db_url.strip() == "":
        diagnostics["database_configured"] = False
        diagnostics["connection_status"] = "not_configured"
        diagnostics["recommendations"].append("DATABASE_URL is not set. Please set it in .env file")
        diagnostics["recommendations"].append("Example: DATABASE_URL=postgresql://user:password@host:port/database")
        return diagnostics
    
    diagnostics["database_configured"] = True
    
    # Mask password in URL for security
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
        pass
    
    diagnostics["configuration"]["url_masked"] = masked_url
    diagnostics["configuration"]["protocol"] = db_url.split("://")[0] if "://" in db_url else "unknown"
    
    # Extract connection details (masked)
    try:
        if "@" in db_url and "://" in db_url:
            parts = db_url.split("://")
            if len(parts) == 2:
                rest = parts[1]
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    if ":" in auth_part:
                        user, _ = auth_part.split(":", 1)
                        diagnostics["configuration"]["user"] = user
                    
                    if ":" in host_part:
                        host, port_db = host_part.split(":", 1)
                        if "/" in port_db:
                            port, db_name = port_db.split("/", 1)
                            diagnostics["configuration"]["host"] = host
                            diagnostics["configuration"]["port"] = port
                            diagnostics["configuration"]["database"] = db_name.split("?")[0] if "?" in db_name else db_name
    except Exception as e:
        diagnostics["configuration"]["parse_error"] = str(e)
    
    # Test connection
    try:
        import asyncio
        connection_result = await asyncio.wait_for(
            db_manager.check_connection(),
            timeout=10.0
        )
        diagnostics["connection_test"] = {
            "success": connection_result,
            "message": "Connection successful" if connection_result else "Connection failed"
        }
        diagnostics["connection_status"] = "connected" if connection_result else "failed"
        
        if not connection_result:
            diagnostics["recommendations"].append("Database connection test failed")
            diagnostics["recommendations"].append("Check if database server is running")
            diagnostics["recommendations"].append("Verify host, port, and database name are correct")
            diagnostics["recommendations"].append("Check network connectivity and firewall rules")
            diagnostics["recommendations"].append("Verify username and password are correct")
    except asyncio.TimeoutError:
        diagnostics["connection_test"] = {
            "success": False,
            "message": "Connection test timed out after 10 seconds"
        }
        diagnostics["connection_status"] = "timeout"
        diagnostics["recommendations"].append("Connection timed out - database server may be unreachable")
        diagnostics["recommendations"].append("Check network connectivity and firewall rules")
        diagnostics["recommendations"].append("Verify database server is running and accessible")
    except Exception as e:
        diagnostics["connection_test"] = {
            "success": False,
            "message": f"Connection test error: {str(e)}",
            "error_type": type(e).__name__
        }
        diagnostics["connection_status"] = "error"
        diagnostics["recommendations"].append(f"Connection error: {str(e)}")

    return diagnostics


@router.get("/dns-test")
async def dns_test() -> Dict[str, Any]:
    """
    Test DNS resolution for database hostname.

    Returns DNS cache statistics and resolution test results.
    Useful for debugging DNS-related connectivity issues.

    Returns:
        dict: DNS resolution status and cache statistics
    """
    from app.utils.dns_resolver import (
        get_dns_cache_stats,
        resolve_hostname,
        DNSResolutionError
    )
    from urllib.parse import urlparse
    import time

    result = {
        "timestamp": datetime.now().isoformat(),
        "hostname": None,
        "resolution_status": None,
        "resolved_ip": None,
        "resolution_time_ms": None,
        "cache_stats": None,
        "error": None
    }

    try:
        # Extract hostname from DATABASE_URL
        parsed = urlparse(settings.database_url)
        hostname = parsed.hostname

        if not hostname:
            result["error"] = "No hostname found in DATABASE_URL"
            return result

        result["hostname"] = hostname

        # Test DNS resolution
        start_time = time.time()
        try:
            resolved_ip = resolve_hostname(hostname, use_cache=False)
            resolution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result["resolution_status"] = "success"
            result["resolved_ip"] = resolved_ip
            result["resolution_time_ms"] = round(resolution_time, 2)
        except DNSResolutionError as dns_error:
            result["resolution_status"] = "failed"
            result["error"] = str(dns_error)
        except Exception as e:
            result["resolution_status"] = "error"
            result["error"] = f"Unexpected error: {str(e)}"

        # Get cache statistics
        result["cache_stats"] = get_dns_cache_stats()

    except Exception as e:
        logger.error(f"Error in DNS test endpoint: {e}", exc_info=True)
        result["error"] = f"Test error: {str(e)}"

    return result
