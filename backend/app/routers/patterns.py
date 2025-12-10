"""
Pattern Analysis API endpoints.

Provides AI-powered pattern detection and stock predictions via cached results.
"""

import logging
import json
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.user import User
from app.core.security import get_current_active_user
from app.core.redis_cache import get_cache
# from app.tasks.analysis_tasks import analyze_company_patterns_task, precompute_top_patterns_task # Moved inside functions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patterns", tags=["Pattern Analysis"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
redis = get_cache()


@router.get("/analyze/{ticker}")
@limiter.limit("30/minute")
async def analyze_company_patterns(
    request: Request,
    ticker: str,
    days_back: int = Query(90, ge=7, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze trading patterns for a specific company.
    
    Checks cache first. If not found, triggers a background analysis task.
    """
    from app.tasks.analysis_tasks import analyze_company_patterns_task # Import here

    try:
        cache_key = f"patterns:{ticker}:{days_back}"
        
        if redis.enabled():
            cached_result = redis.get(cache_key)
            if cached_result:
                # Redis returns parsed JSON if it was stored as such by our wrapper, 
                # or we might need to handle it. get_cache().get() typically handles JSON loads.
                return cached_result

        # If not in cache, trigger background task
        analyze_company_patterns_task.delay(ticker, days_back)
        
        # Return 202 Accepted to indicate processing
        return {
            "status": "processing",
            "message": f"Analysis for {ticker} has been queued. Please check back shortly.",
            "ticker": ticker
        }

    except Exception as e:
        logger.error(f"Error serving pattern analysis for {ticker}: {e}", exc_info=True)
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
):
    """
    Get top companies with specific trading patterns from cache.
    """
    valid_patterns = ["BUYING_MOMENTUM", "SELLING_PRESSURE", "CLUSTER", "REVERSAL"]

    if pattern_type.upper() not in valid_patterns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pattern type. Must be one of: {', '.join(valid_patterns)}",
        )

    try:
        cache_key = f"patterns:top:{pattern_type.upper()}"
        
        if redis.enabled():
            cached_results = redis.get(cache_key)
            if cached_results:
                # Limit the results if needed
                return {
                    "pattern_type": pattern_type.upper(),
                    "companies": cached_results[:limit],
                    "count": len(cached_results[:limit]),
                }
        
        # If cache miss, trigger pre-computation (this might take a while, so return empty for now)
        from app.tasks.analysis_tasks import precompute_top_patterns_task # Import here
        precompute_top_patterns_task.delay()
        
        return {
            "pattern_type": pattern_type.upper(),
            "companies": [],
            "count": 0,
            "message": "Pattern analysis is being updated. Please check back later."
        }

    except Exception as e:
        logger.error(
            f"Error getting top patterns for {pattern_type}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )
