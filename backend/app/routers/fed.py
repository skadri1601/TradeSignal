"""
Federal Reserve Data API Router

Endpoints for FED meetings, rate decisions, and economic indicators.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Request, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.fed_data_service import FedDataService
from app.models.user import User
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fed", tags=["Federal Reserve"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get("/calendar")
@limiter.limit("30/minute")
async def get_fed_calendar(
    request: Request,
    months_ahead: int = Query(6, ge=1, le=12, description="Months to look ahead"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get FED calendar with upcoming meetings and economic data releases.

    Returns:
        List of FED-related events (FOMC meetings, CPI releases, employment reports)
    """
    try:
        service = FedDataService()
        calendar = await service.get_fed_calendar(months_ahead=months_ahead)
        return {
            "events": calendar,
            "count": len(calendar),
            "months_ahead": months_ahead,
        }
    except Exception as e:
        logger.error(f"Error in get_fed_calendar endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch FED calendar. Please try again later.",
        )


@router.get("/interest-rate")
@limiter.limit("30/minute")
async def get_current_interest_rate(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current Federal Reserve interest rate.

    Returns:
        Current interest rate and date
    """
    try:
        service = FedDataService()
        rate_data = await service.get_current_interest_rate()

        if not rate_data:
            raise HTTPException(
                status_code=503,
                detail="Interest rate data unavailable. Cache empty or FRED_API_KEY not configured for background tasks.",
            )

        return rate_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_interest_rate endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch interest rate data. Please try again later.",
        )


@router.get("/rate-history")
@limiter.limit("30/minute")
async def get_rate_history(
    request: Request,
    days_back: int = Query(365, ge=30, le=3650, description="Days of history"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get Federal Reserve interest rate history.

    Returns:
        Historical interest rate data
    """
    try:
        service = FedDataService()
        history = await service.get_rate_history(days_back=days_back)
        if not history:
            raise HTTPException(
                status_code=503,
                detail="Interest rate history data unavailable. Cache empty or FRED_API_KEY not configured for background tasks.",
            )
        return {"history": history, "count": len(history), "days_back": days_back}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_rate_history endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch rate history. Please try again later.",
        )


@router.get("/economic-indicators")
@limiter.limit("30/minute")
async def get_economic_indicators(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get key economic indicators (inflation, unemployment, GDP, retail sales).

    Returns:
        Current economic indicator values
    """
    try:
        service = FedDataService()
        indicators = await service.get_economic_indicators()
        if not indicators:
            raise HTTPException(
                status_code=503,
                detail="Economic indicators data unavailable. Cache empty or FRED_API_KEY not configured for background tasks.",
            )
        return {"indicators": indicators, "last_updated": datetime.now(timezone.utc).isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_economic_indicators endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch economic indicators. Please try again later.",
        )
