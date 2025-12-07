"""
Earnings API Router

Endpoints for earnings announcements, estimates, and calendar.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.earnings_service import EarningsService
from app.models.user import User
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/earnings", tags=["Earnings"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get("/company/{ticker}")
@limiter.limit("30/minute")
async def get_company_earnings(
    request: Request,
    ticker: str,
    quarters: int = Query(8, ge=1, le=20, description="Number of quarters to fetch"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get earnings data for a specific company.

    Returns:
        Earnings history, upcoming dates, estimates, surprises
    """
    service = EarningsService(db)
    result = await service.get_company_earnings(ticker, quarters=quarters)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=result["error"]
        )

    return result


@router.get("/calendar")
@limiter.limit("30/minute")
async def get_earnings_calendar(
    request: Request,
    days_ahead: int = Query(30, ge=1, le=90, description="Days to look ahead"),
    limit: int = Query(100, ge=1, le=500, description="Maximum companies to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get earnings calendar for all companies.

    Returns:
        List of companies with upcoming earnings dates
    """
    service = EarningsService(db)
    calendar = await service.get_earnings_calendar(days_ahead=days_ahead, limit=limit)
    return {"earnings": calendar, "count": len(calendar), "days_ahead": days_ahead}
