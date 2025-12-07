"""
Federal Reserve Data API Router

Endpoints for FED meetings, rate decisions, and economic indicators.
"""

import logging
from datetime import datetime
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
    db: AsyncSession = Depends(get_db),
):
    """
    Get FED calendar with upcoming meetings and economic data releases.

    Returns:
        List of FED-related events (FOMC meetings, CPI releases, employment reports)
    """
    try:
        service = FedDataService(db)
        calendar = await service.get_fed_calendar(months_ahead=months_ahead)
        return {
            "events": calendar,
            "count": len(calendar),
            "months_ahead": months_ahead,
        }
    except Exception as e:
        logger.error(f"Error in get_fed_calendar endpoint: {e}", exc_info=True)
        # Service already handles cache fallback
        try:
            service = FedDataService(db)
            calendar = await service.get_fed_calendar(months_ahead=months_ahead)
            return {
                "events": calendar,
                "count": len(calendar),
                "months_ahead": months_ahead,
                "note": "Data may be from cache due to API error",
            }
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch FED calendar. Please try again later.",
            )


@router.get("/interest-rate")
@limiter.limit("30/minute")
async def get_current_interest_rate(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current Federal Reserve interest rate.

    Returns:
        Current interest rate and date
    """
    try:
        service = FedDataService(db)
        rate_data = await service.get_current_interest_rate()

        if not rate_data:
            return {
                "error": "Interest rate data unavailable. Configure FRED_API_KEY in .env or check API status.",
                "cached": False,
            }

        return rate_data
    except Exception as e:
        logger.error(f"Error in get_current_interest_rate endpoint: {e}", exc_info=True)
        # Try to return cached data if available
        try:
            service = FedDataService(db)
            # Service already handles cache fallback, but we can add a message
            rate_data = await service.get_current_interest_rate()
            if rate_data:
                return rate_data
        except Exception:
            pass
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
    db: AsyncSession = Depends(get_db),
):
    """
    Get Federal Reserve interest rate history.

    Returns:
        Historical interest rate data
    """
    try:
        service = FedDataService(db)
        history = await service.get_rate_history(days_back=days_back)
        return {"history": history, "count": len(history), "days_back": days_back}
    except Exception as e:
        logger.error(f"Error in get_rate_history endpoint: {e}", exc_info=True)
        # Service already handles cache fallback
        try:
            service = FedDataService(db)
            history = await service.get_rate_history(days_back=days_back)
            return {
                "history": history,
                "count": len(history),
                "days_back": days_back,
                "note": "Data may be from cache due to API error",
            }
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch rate history. Please try again later.",
            )


@router.get("/economic-indicators")
@limiter.limit("30/minute")
async def get_economic_indicators(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get key economic indicators (inflation, unemployment, GDP, retail sales).

    Returns:
        Current economic indicator values
    """
    try:
        service = FedDataService(db)
        indicators = await service.get_economic_indicators()
        return {"indicators": indicators, "last_updated": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error in get_economic_indicators endpoint: {e}", exc_info=True)
        # Service already handles cache fallback
        try:
            service = FedDataService(db)
            indicators = await service.get_economic_indicators()
            return {
                "indicators": indicators,
                "last_updated": datetime.utcnow().isoformat(),
                "note": "Data may be from cache due to API error",
            }
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch economic indicators. Please try again later.",
            )
