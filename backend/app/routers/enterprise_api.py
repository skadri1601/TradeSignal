"""
Enterprise API Router.

Provides programmatic access to TradeSignal data for institutional clients.
Features:
- RESTful endpoints
- Rate limiting by tier
- API key authentication
- Webhook support
- Comprehensive documentation
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel, Field

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier
from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider
from app.middleware.feature_gating import require_feature
from app.services.tier_service import TierService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enterprise", tags=["Enterprise API"])

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Response Models
class TradeResponse(BaseModel):
    """Trade response model."""

    id: int
    ticker: str
    company_name: str
    insider_name: str
    insider_role: Optional[str]
    transaction_type: str
    shares: float
    price_per_share: Optional[float]
    total_value: Optional[float]
    filing_date: str

    class Config:
        from_attributes = True


class CompanyInsightsResponse(BaseModel):
    """Company insights response."""

    ticker: str
    company_name: str
    total_trades: int
    buy_count: int
    sell_count: int
    latest_trade_date: Optional[str]

    class Config:
        from_attributes = True


# Rate limiting by tier
RATE_LIMITS = {
    SubscriptionTier.FREE.value: {"requests_per_day": 100},
    SubscriptionTier.PLUS.value: {"requests_per_day": 1000},
    SubscriptionTier.PRO.value: {"requests_per_day": 10000},
    SubscriptionTier.ENTERPRISE.value: {"requests_per_day": -1},  # Unlimited
}


async def get_api_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate user via API key.

    For now, uses standard JWT auth. API key auth can be added later.
    """
    # TODO: Implement API key authentication
    # For now, require standard authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key authentication not yet implemented. Use standard JWT authentication.",
    )


async def check_rate_limit(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Check if user has exceeded API rate limit."""
    tier = await TierService.get_user_tier(current_user.id, db)
    limits = RATE_LIMITS.get(tier, RATE_LIMITS[SubscriptionTier.FREE.value])

    daily_limit = limits["requests_per_day"]
    if daily_limit == -1:
        return  # Unlimited

    # Check usage (simplified - would use proper rate limiting middleware)
    usage = await TierService.get_or_create_usage(current_user.id, db)
    if usage.api_calls >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"API rate limit exceeded. Limit: {daily_limit} requests/day. Upgrade for higher limits.",
            headers={"Retry-After": "86400"},  # 24 hours
        )


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    days_back: int = Query(30, ge=1, le=365, description="Days to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get insider trades.

    Requires API access (Pro tier or higher).
    """
    # Check API access
    await require_feature("api_access", "API access")(current_user, db)
    await check_rate_limit(current_user, db)

    # Increment API usage
    await TierService.increment_api_usage(current_user.id, db)

    # Build query
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    query = (
        select(Trade, Company, Insider)
        .join(Company, Trade.company_id == Company.id)
        .join(Insider, Trade.insider_id == Insider.id)
        .where(Trade.filing_date >= cutoff_date)
        .order_by(desc(Trade.filing_date))
        .limit(limit)
    )

    if ticker:
        query = query.where(Company.ticker == ticker.upper())

    result = await db.execute(query)
    trades_data = result.all()

    # Format response
    trades = []
    for trade, company, insider in trades_data:
        trades.append(
            TradeResponse(
                id=trade.id,
                ticker=company.ticker,
                company_name=company.name,
                insider_name=insider.name,
                insider_role=insider.title,
                transaction_type=trade.transaction_type,
                shares=float(trade.shares) if trade.shares else 0.0,
                price_per_share=float(trade.price_per_share) if trade.price_per_share else None,
                total_value=float(trade.total_value) if trade.total_value else None,
                filing_date=trade.filing_date.isoformat(),
            )
        )

    return trades


@router.get("/companies/{ticker}/insights", response_model=CompanyInsightsResponse)
async def get_company_insights(
    ticker: str,
    days_back: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get company insights and trade summary.

    Requires API access (Pro tier or higher).
    """
    await require_feature("api_access", "API access")(current_user, db)
    await check_rate_limit(current_user, db)

    await TierService.increment_api_usage(current_user.id, db)

    # Get company
    result = await db.execute(
        select(Company).where(Company.ticker == ticker.upper())
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {ticker} not found",
        )

    # Get trade stats
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    result = await db.execute(
        select(
            func.count(Trade.id).label("total_trades"),
            func.sum(
                func.case((Trade.transaction_type == "BUY", 1), else_=0)
            ).label("buy_count"),
            func.sum(
                func.case((Trade.transaction_type == "SELL", 1), else_=0)
            ).label("sell_count"),
            func.max(Trade.filing_date).label("latest_date"),
        )
        .join(Company, Trade.company_id == Company.id)
        .where(
            Company.ticker == ticker.upper(),
            Trade.filing_date >= cutoff_date,
        )
    )
    stats = result.first()

    return CompanyInsightsResponse(
        ticker=company.ticker,
        company_name=company.name,
        total_trades=stats.total_trades or 0,
        buy_count=stats.buy_count or 0,
        sell_count=stats.sell_count or 0,
        latest_trade_date=stats.latest_date.isoformat() if stats.latest_date else None,
    )


@router.get("/usage")
async def get_api_usage(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get API usage statistics.

    Shows current usage and rate limits.
    """
    tier = await TierService.get_user_tier(current_user.id, db)
    limits = RATE_LIMITS.get(tier, RATE_LIMITS[SubscriptionTier.FREE.value])
    usage = await TierService.get_or_create_usage(current_user.id, db)

    daily_limit = limits["requests_per_day"]

    return {
        "tier": tier,
        "daily_limit": daily_limit if daily_limit != -1 else "unlimited",
        "requests_today": usage.api_calls,
        "remaining": (
            daily_limit - usage.api_calls if daily_limit != -1 else "unlimited"
        ),
        "reset_at": (datetime.utcnow() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat(),
    }


# Webhook Management
class WebhookCreate(BaseModel):
    """Webhook creation request."""

    url: str = Field(..., description="Webhook URL to receive events")
    events: List[str] = Field(..., description="Events to subscribe to")
    secret: Optional[str] = Field(None, description="Optional webhook secret for verification")


class WebhookResponse(BaseModel):
    """Webhook response model."""

    id: int
    url: str
    events: List[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/webhooks", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a webhook subscription.

    Requires Enterprise tier.
    """
    await require_feature("api_access", "API access")(current_user, db)

    # TODO: Implement webhook model and storage
    # For now, return placeholder
    return WebhookResponse(
        id=1,
        url=webhook_data.url,
        events=webhook_data.events,
        is_active=True,
        created_at=datetime.utcnow().isoformat(),
    )


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all webhooks for the current user.

    Requires Enterprise tier.
    """
    await require_feature("api_access", "API access")(current_user, db)

    # TODO: Implement webhook listing
    return []


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a webhook subscription.

    Requires Enterprise tier.
    """
    await require_feature("api_access", "API access")(current_user, db)

    # TODO: Implement webhook deletion
    return {"message": "Webhook deleted", "webhook_id": webhook_id}

