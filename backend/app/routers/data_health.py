from fastapi import APIRouter, status as http_status
import os
import logging
from typing import Dict, Any
from datetime import datetime

from app.config import settings
from app.database import db_manager

# NOTE: Redis cache removed - caching now uses Supabase
from app.services.congressional_client import CongressionalAPIClient
from app.models.scrape_history import ScrapeHistory # Import ScrapeHistory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-health", tags=["data-health"])

REQUIRED_ENV_VARS_CRITICAL = [
    "DATABASE_URL",
    "FINNHUB_API_KEY",
    "GEMINI_API_KEY",
    "PUSH_VAPID_PRIVATE_KEY",
    "PUSH_VAPID_CLAIMS_EMAIL",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "SUPERUSER_EMAIL",
    "SUPERUSER_PASSWORD",
]


@router.get("/")
async def data_health_check() -> Dict[str, Any]:
    """
    Provides a comprehensive health check for all data-related components,
    including environment variables, Finnhub API, and Congressional data sources.
    """
    overall_status = "healthy"
    details: Dict[str, Any] = {}

    # 1. Environment Variable Check
    env_vars_status = "healthy"
    missing_vars = [var for var in REQUIRED_ENV_VARS_CRITICAL if not os.getenv(var)]
    if missing_vars:
        env_vars_status = "unhealthy"
        overall_status = "degraded"
        details["env_variables"] = {
            "status": env_vars_status,
            "missing": missing_vars,
            "message": "Critical environment variables are missing.",
        }
        logger.error(f"Missing critical environment variables: {', '.join(missing_vars)}")
    else:
        details["env_variables"] = {"status": env_vars_status, "message": "All critical environment variables are set."}

    # 2. Finnhub API Key Status
    finnhub_api_key_configured = bool(settings.finnhub_api_key)
    finnhub_api_status = "configured" if finnhub_api_key_configured else "not configured"
    finnhub_api_message = "FINNHUB_API_KEY is set." if finnhub_api_key_configured else "FINNHUB_API_KEY is not set. Primary source unavailable."
    
    details["finnhub_api"] = {
        "status": finnhub_api_status,
        "message": finnhub_api_message
    }
    if not finnhub_api_key_configured:
        overall_status = "degraded"

    # 3. Congressional Client Status (primary vs. fallback)
    congressional_client_config = {
        "use_fallback_sources_enabled": settings.use_fallback_sources,
        "fallback_max_age_days": settings.congressional_fallback_max_age_days
    }
    details["congressional_client_config"] = congressional_client_config

    # Get last successful congressional scrape timestamp
    last_scrape_timestamp = None
    try:
        async with db_manager.get_session() as session:
            latest_congressional_scrape = (
                await session.execute(
                    ScrapeHistory.__table__.select()
                    .where(ScrapeHistory.job_type == "congressional_trades")
                    .order_by(ScrapeHistory.timestamp.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            if latest_congressional_scrape:
                last_scrape_timestamp = latest_congressional_scrape.timestamp.isoformat()
    except Exception as e:
        logger.error(f"Error fetching last congressional scrape history: {e}")
        details["congressional_client_runtime"] = {"status": "error", "message": f"Failed to get scrape history: {e}"}
        overall_status = "degraded"

    data_source_in_use = "Finnhub (Primary)"
    if not finnhub_api_key_configured and settings.use_fallback_sources:
        data_source_in_use = "Fallback Sources"
    elif not finnhub_api_key_configured and not settings.use_fallback_sources:
        data_source_in_use = "None (No API Key & Fallback Disabled)"
        overall_status = "degraded"
    elif finnhub_api_key_configured and settings.use_fallback_sources:
        data_source_in_use = "Finnhub (Primary) with Fallback Enabled"

    details["congressional_client_runtime"] = {
        "status": "active",
        "primary_source_configured": finnhub_api_key_configured,
        "fallback_sources_enabled": settings.use_fallback_sources,
        "data_source_being_used": data_source_in_use,
        "last_successful_data_fetch": last_scrape_timestamp,
        "message": "Congressional data source status.",
    }
    
    # 4. Database Check (re-using db_manager from health.py)
    try:
        db_healthy = await db_manager.check_connection()
        if db_healthy:
            details["database"] = {"status": "healthy", "message": "PostgreSQL connection OK"}
        else:
            details["database"] = {"status": "unhealthy", "message": "PostgreSQL connection failed"}
            overall_status = "degraded"
    except Exception as e:
        details["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"
        logger.error(f"Database health check failed in data_health: {e}")

    # Redis has been removed - now using Supabase caching
    details["cache"] = {
        "status": "disabled",
        "message": "Redis removed - using Supabase caching instead"
    }


    http_status_code = http_status.HTTP_200_OK if overall_status == "healthy" else http_status.HTTP_503_SERVICE_UNAVAILABLE

    return {"overall_status": overall_status, "details": details}, http_status_code
