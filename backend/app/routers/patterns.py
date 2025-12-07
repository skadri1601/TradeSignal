"""
Pattern Analysis API endpoints.

Provides AI-powered pattern detection and stock predictions.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.pattern_analysis_service import PatternAnalysisService
from app.models.user import User
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patterns", tags=["Pattern Analysis"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get("/analyze/{ticker}")
@limiter.limit("30/minute")
async def analyze_company_patterns(
    request: Request,
    ticker: str,
    days_back: int = Query(90, ge=7, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze trading patterns for a specific company.

    Detects:
    - Buying momentum
    - Selling pressure
    - Insider clusters
    - Pattern reversals

    Returns predictions and recommendations.
    """
    try:
        service = PatternAnalysisService(db)
        result = await service.analyze_company_patterns(ticker, days_back)

        if "error" in result:
            # Check if it's a database connection error
            if (
                "connection" in result["error"].lower()
                or "database" in result["error"].lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection error. Please try again later.",
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing patterns for {ticker}: {e}", exc_info=True)
        # Check if it's a database-related error
        error_str = str(e).lower()
        if "connection" in error_str or "database" in error_str or "pool" in error_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error. Please try again later.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )


@router.get("/top/{pattern_type}")
@limiter.limit("30/minute")
async def get_top_patterns(
    request: Request,
    pattern_type: str = Path(
        ...,
        description="Pattern type: BUYING_MOMENTUM, SELLING_PRESSURE, CLUSTER, REVERSAL",
    ),
    limit: int = Query(10, ge=1, le=50, description="Number of companies to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top companies with specific trading patterns.

    Pattern types:
    - BUYING_MOMENTUM: Strong insider buying activity
    - SELLING_PRESSURE: Significant insider selling
    - CLUSTER: Multiple insiders trading together
    - REVERSAL: Pattern changes/reversals
    """
    valid_patterns = ["BUYING_MOMENTUM", "SELLING_PRESSURE", "CLUSTER", "REVERSAL"]

    if pattern_type.upper() not in valid_patterns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pattern type. Must be one of: {', '.join(valid_patterns)}",
        )

    try:
        service = PatternAnalysisService(db)
        results = await service.get_top_patterns(pattern_type.upper(), limit)

        return {
            "pattern_type": pattern_type.upper(),
            "companies": results,
            "count": len(results),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting top patterns for {pattern_type}: {e}", exc_info=True
        )
        # Check if it's a database-related error
        error_str = str(e).lower()
        if "connection" in error_str or "database" in error_str or "pool" in error_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error. Please try again later.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )
