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
            detail="AI service unavailable. Please check AI provider configuration.",
        )

    if "error" in result:
        error_detail = result["error"]
        # Include diagnostics if available
        if "diagnostics" in result:
            diag = result["diagnostics"]
            error_detail += (
                f" Diagnostics: {diag.get('total_trades_in_db', 0)} total trades in DB, "
                f"{diag.get('trades_in_last_30_days', 0)} trades in last 30 days."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
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
            detail="AI service unavailable. Please check AI provider configuration.",
        )

    if "error" in result:
        error_detail = result["error"]
        # Include diagnostics if available
        if "diagnostics" in result:
            diag = result["diagnostics"]
            error_detail += (
                f" Diagnostics: {diag.get('total_trades_in_db', 0)} total trades in DB, "
                f"{diag.get('companies_with_trades', 0)} companies with trades, "
                f"{diag.get('companies_meeting_criteria', 0)} companies meeting criteria (>=3 trades)."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        )

    return result


@router.get("/diagnostics", summary="Get AI insights diagnostic information")
@limiter.limit("10/minute")
async def get_ai_diagnostics(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get diagnostic information about database state and AI insights configuration.
    
    Useful for troubleshooting "no data" issues in Daily Summary and Trading Signals.
    
    **Returns:**
    - Trade counts by date range
    - Company counts
    - AI configuration
    - Date range settings
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select, func
    from app.models.trade import Trade
    from app.models.company import Company
    
    try:
        # Get total trades count
        total_trades_result = await db.execute(select(func.count(Trade.id)))
        total_trades = total_trades_result.scalar() or 0
        
        # Get trades by date ranges
        now = datetime.utcnow()
        days_back = getattr(settings, 'ai_insights_days_back', 7)
        
        cutoff_7d = now - timedelta(days=7)
        cutoff_30d = now - timedelta(days=30)
        cutoff_90d = now - timedelta(days=90)
        cutoff_configured = now - timedelta(days=days_back)
        
        trades_7d_result = await db.execute(
            select(func.count(Trade.id)).where(Trade.filing_date >= cutoff_7d)
        )
        trades_7d = trades_7d_result.scalar() or 0
        
        trades_30d_result = await db.execute(
            select(func.count(Trade.id)).where(Trade.filing_date >= cutoff_30d)
        )
        trades_30d = trades_30d_result.scalar() or 0
        
        trades_90d_result = await db.execute(
            select(func.count(Trade.id)).where(Trade.filing_date >= cutoff_90d)
        )
        trades_90d = trades_90d_result.scalar() or 0
        
        trades_configured_result = await db.execute(
            select(func.count(Trade.id)).where(Trade.filing_date >= cutoff_configured)
        )
        trades_configured = trades_configured_result.scalar() or 0
        
        # Get companies with trades in configured range
        companies_with_trades_result = await db.execute(
            select(func.count(func.distinct(Trade.company_id)))
            .where(Trade.filing_date >= cutoff_configured)
        )
        companies_with_trades = companies_with_trades_result.scalar() or 0
        
        # Get companies with >=3 trades (for trading signals)
        companies_meeting_criteria_result = await db.execute(
            select(
                func.count(func.distinct(Trade.company_id))
            )
            .select_from(Trade)
            .where(Trade.filing_date >= cutoff_configured)
            .group_by(Trade.company_id)
            .having(func.count(Trade.id) >= 3)
        )
        companies_meeting_criteria = len(companies_meeting_criteria_result.all()) if companies_meeting_criteria_result else 0
        
        # Get total companies
        total_companies_result = await db.execute(select(func.count(Company.id)))
        total_companies = total_companies_result.scalar() or 0
        
        # Get oldest and newest trade dates
        oldest_trade_result = await db.execute(
            select(func.min(Trade.filing_date))
        )
        oldest_trade_date = oldest_trade_result.scalar()
        
        newest_trade_result = await db.execute(
            select(func.max(Trade.filing_date))
        )
        newest_trade_date = newest_trade_result.scalar()
        
        return {
            "database": {
                "total_trades": total_trades,
                "total_companies": total_companies,
                "oldest_trade_date": oldest_trade_date.isoformat() if oldest_trade_date else None,
                "newest_trade_date": newest_trade_date.isoformat() if newest_trade_date else None,
            },
            "trades_by_period": {
                "last_7_days": trades_7d,
                "last_30_days": trades_30d,
                "last_90_days": trades_90d,
                f"last_{days_back}_days_configured": trades_configured,
            },
            "companies": {
                "total": total_companies,
                f"with_trades_in_last_{days_back}_days": companies_with_trades,
                "meeting_trading_signals_criteria": companies_meeting_criteria,
            },
            "configuration": {
                "ai_insights_days_back": days_back,
                "ai_provider": settings.ai_provider,
                "gemini_configured": settings.gemini_api_key is not None,
                "openai_configured": settings.openai_api_key is not None,
                "ai_insights_enabled": settings.enable_ai_insights,
            },
            "current_time_utc": now.isoformat(),
            "cutoff_date_configured": cutoff_configured.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error generating diagnostics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating diagnostics: {str(e)}"
        )


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
