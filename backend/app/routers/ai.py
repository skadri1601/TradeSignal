"""
AI Insights API endpoints for TradeSignal.

Provides AI-powered analysis of insider trading patterns using configured AI providers.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.ai_service import AIService
from app.services.tier_service import TierService
from app.schemas.ai import (
    CompanyAnalysisResponse,
    DailySummaryResponse,
    ChatQuestion,
    ChatResponse,
    TradingSignalsResponse,
)
from app.config import settings
from app.models.user import User
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Insights"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def check_ai_availability():
    """Dependency to check if AI insights are enabled and a provider is configured."""
    if not settings.enable_ai_insights:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI insights feature is disabled. Set ENABLE_AI_INSIGHTS=true in .env",
        )
    if not settings.gemini_api_key and not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No AI provider API key configured. Set GEMINI_API_KEY or OPENAI_API_KEY in .env",
        )


@router.get(
    "/analyze/{ticker}",
    response_model=CompanyAnalysisResponse,
    summary="Analyze company insider trading",
    dependencies=[Depends(check_ai_availability)],
)
@limiter.limit("5/hour")  # AI is expensive, limit to 5 requests per hour
async def analyze_company(
    request: Request,
    ticker: str,
    days_back: int = Query(30, ge=1, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-powered analysis of insider trading for a specific company.

    Analyzes recent trading patterns, identifies sentiment (bullish/bearish/neutral),
    and provides key insights about insider activity.

    - **ticker**: Company ticker symbol (e.g., NVDA, TSLA)
    - **days_back**: Number of days to analyze (1-365, default: 30)

    **Requires:**
    - AI provider API key configured
    - AI insights feature enabled

    **Returns:**
    - AI-generated analysis with sentiment and insights
    """
    # Check tier limit
    await TierService.check_ai_limit(current_user.id, db)

    service = AIService(db)
    result = await service.analyze_company(ticker.upper(), days_back)

    # Increment usage counter
    await TierService.increment_ai_usage(current_user.id, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    if "error" in result and result.get("ticker") is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"]
        )

    return result


@router.get(
    "/summary/daily",
    response_model=DailySummaryResponse,
    summary="Get daily insider trading summary",
    dependencies=[Depends(check_ai_availability)],
)
@limiter.limit("10/hour")
async def get_daily_summary(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-generated summary of top insider trades from the last 24 hours.

    Highlights the most significant trades and provides context about what
    investors should know.

    **Requires:**
    - AI provider API key configured
    - AI insights feature enabled

    **Returns:**
    - AI-written summary with top trades
    """
    # Check tier limit
    await TierService.check_ai_limit(current_user.id, db)

    service = AIService(db)
    result = await service.generate_daily_summary()

    # Increment usage counter
    await TierService.increment_ai_usage(current_user.id, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"]
        )

    return result


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Ask AI about insider trades",
    dependencies=[Depends(check_ai_availability)],
)
@limiter.limit("20/hour")
async def ask_question(
    request: Request,
    question_data: ChatQuestion,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ask natural language questions about insider trading data.

    Examples:
    - "Which companies have the most insider buying this month?"
    - "Explain why NVDA insiders are selling"
    - "What are the biggest trades today?"

    **Requires:**
    - AI provider API key configured
    - AI insights feature enabled

    **Returns:**
    - AI-generated answer to your question
    """
    # Check tier limit
    await TierService.check_ai_limit(current_user.id, db)

    service = AIService(db)
    result = await service.ask_question(question_data.question)

    # Increment usage counter
    await TierService.increment_ai_usage(current_user.id, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"]
        )

    return result


@router.get(
    "/signals",
    response_model=TradingSignalsResponse,
    summary="Get AI trading signals",
    dependencies=[Depends(check_ai_availability)],
)
@limiter.limit("10/hour")
async def get_trading_signals(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-generated trading signals based on recent insider activity.

    Analyzes companies with significant insider trading in the last 7 days
    and provides bullish/bearish/neutral signals.

    **Signal Types:**
    - BULLISH: High insider buying activity
    - BEARISH: High insider selling activity
    - NEUTRAL: Mixed or balanced activity

    **Strength Levels:**
    - STRONG: Very clear signal (>85% buy or <15% buy)
    - MODERATE: Clear signal (70-85% buy or 15-30% buy)
    - WEAK: Unclear signal (30-70% buy)

    **Requires:**
    - AI provider API key configured
    - AI insights feature enabled

    **Returns:**
    - List of trading signals for companies with high activity
    """
    # Check tier limit
    await TierService.check_ai_limit(current_user.id, db)

    service = AIService(db)
    result = await service.generate_trading_signals()

    # Increment usage counter
    await TierService.increment_ai_usage(current_user.id, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"]
        )

    return result


@router.get("/status", summary="Check AI service status")
@limiter.limit("30/minute")
async def get_ai_status(request: Request):
    """
    Check if AI insights service is available.

    **Returns:**
    - Service status and configuration
    """
    gemini_configured = settings.gemini_api_key is not None
    openai_configured = settings.openai_api_key is not None

    provider_status = {
        "primary": settings.ai_provider,
        "gemini": {
            "configured": gemini_configured,
            "model": settings.gemini_model if gemini_configured else None,
        },
        "openai": {
            "configured": openai_configured,
            "model": settings.openai_model if openai_configured else None,
        },
    }

    available = settings.enable_ai_insights and (gemini_configured or openai_configured)

    return {
        "enabled": settings.enable_ai_insights,
        "available": available,
        "providers": provider_status,
        "active_provider": settings.ai_provider if available else None,
    }
