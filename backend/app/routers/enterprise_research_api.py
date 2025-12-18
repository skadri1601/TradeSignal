"""
Enterprise Research API Router.

RESTful endpoints for all research features (IVT, Risk Levels, Management Scores, etc.)
with pricing tiers, developer portal, webhooks.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subscription import SubscriptionTier
from app.middleware.feature_gating import require_feature
from app.services.tier_service import TierService
from app.services.tier_service import TierService
from app.services.dcf_service import DCFService
from app.services.risk_level_service import RiskLevelService
from app.services.management_score_service import ManagementScoreService
from app.services.competitive_strength_service import CompetitiveStrengthService
from app.services.ts_score_service import TSScoreService
from app.models.intrinsic_value import IntrinsicValueTarget
from app.models.risk_level import RiskLevelAssessment
from app.models.management_score import ManagementScore
from app.models.competitive_strength import CompetitiveStrengthRating
from app.models.tradesignal_score import TradeSignalScore
from app.schemas.research import (
    IVTResponse,
    RiskLevelResponse,
    ManagementScoreResponse,
    CompetitiveStrengthResponse,
    TSScoreResponse,
    ComprehensiveResearchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enterprise/research", tags=["Enterprise Research API"])

# Research API pricing tiers
RESEARCH_API_TIERS = {
    SubscriptionTier.PRO.value: {
        "requests_per_month": 1000,
        "features": ["ivt", "risk_levels", "ts_score"],
    },
    SubscriptionTier.ENTERPRISE.value: {
        "requests_per_month": -1,  # Unlimited
        "features": ["ivt", "risk_levels", "management_scores", "competitive_strength", "ts_score"],
    },
}


@router.get("/ivt/{ticker}", response_model=IVTResponse)
async def get_intrinsic_value_target(
    ticker: str,
    current_user: User = Depends(require_feature("research_api", "Research API access")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Intrinsic Value Target (IVT) for a stock.

    Requires Research Pro or Enterprise tier.
    """
    await _check_research_api_limit(current_user, db)

    dcf_service = DCFService(db)
    ivt = await dcf_service.get_latest_ivt(ticker)

    if not ivt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVT not found for {ticker}. Run calculation first.",
        )

    await TierService.increment_api_usage(current_user.id, db)

    return {
        "ticker": ticker,
        "intrinsic_value": float(ivt.intrinsic_value),
        "current_price": float(ivt.current_price),
        "discount_premium_pct": float(ivt.discount_premium_pct),
        "wacc": float(ivt.wacc),
        "terminal_growth_rate": float(ivt.terminal_growth_rate),
        "calculated_at": ivt.calculated_at.isoformat(),
    }


@router.get("/risk-level/{ticker}", response_model=RiskLevelResponse)
async def get_risk_level(
    ticker: str,
    current_user: User = Depends(require_feature("research_api", "Research API access")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get risk level assessment for a stock.

    Requires Research Pro or Enterprise tier.
    """
    await _check_research_api_limit(current_user, db)

    risk_service = RiskLevelService(db)
    risk_assessment = await risk_service.get_latest_risk_level(ticker)

    if not risk_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk assessment not found for {ticker}",
        )

    await TierService.increment_api_usage(current_user.id, db)

    return {
        "ticker": ticker,
        "risk_level": risk_assessment.risk_level,
        "score": float(risk_assessment.score),
        "component_scores": {
            "earnings_volatility": float(risk_assessment.earnings_volatility_score),
            "financial_leverage": float(risk_assessment.financial_leverage_score),
            "operating_leverage": float(risk_assessment.operating_leverage_score),
            "concentration": float(risk_assessment.concentration_score),
            "industry_stability": float(risk_assessment.industry_stability_score),
        },
        "calculated_at": risk_assessment.calculated_at.isoformat(),
    }


@router.get("/management-score/{ticker}", response_model=ManagementScoreResponse)
async def get_management_score(
    ticker: str,
    current_user: User = Depends(require_feature("research_api", "Research API access")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get management excellence score for a stock.

    Requires Enterprise tier.
    """
    await _check_research_api_limit(current_user, db)

    tier = await TierService.get_user_tier(current_user.id, db)
    if tier != SubscriptionTier.ENTERPRISE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management scores require Enterprise tier",
        )

    management_service = ManagementScoreService(db)
    score = await management_service.get_latest_score(ticker)

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Management score not found for {ticker}",
        )

    await TierService.increment_api_usage(current_user.id, db)

    return {
        "ticker": ticker,
        "grade": score.grade,
        "composite_score": float(score.composite_score),
        "component_scores": {
            "m_and_a": float(score.m_and_a_score),
            "capital_discipline": float(score.capital_discipline_score),
            "shareholder_returns": float(score.shareholder_returns_score),
            "leverage_management": float(score.leverage_management_score),
            "governance": float(score.governance_score),
        },
        "calculated_at": score.calculated_at.isoformat(),
    }


@router.get("/competitive-strength/{ticker}", response_model=CompetitiveStrengthResponse)
async def get_competitive_strength(
    ticker: str,
    current_user: User = Depends(require_feature("research_api", "Research API access")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get competitive strength rating for a stock.

    Requires Enterprise tier.
    """
    await _check_research_api_limit(current_user, db)

    tier = await TierService.get_user_tier(current_user.id, db)
    if tier != SubscriptionTier.ENTERPRISE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Competitive strength ratings require Enterprise tier",
        )

    strength_service = CompetitiveStrengthService(db)
    rating = await strength_service.get_latest_rating(ticker)

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competitive strength rating not found for {ticker}",
        )

    await TierService.increment_api_usage(current_user.id, db)

    return {
        "ticker": ticker,
        "rating": rating.rating,
        "composite_score": float(rating.composite_score),
        "component_scores": {
            "network_effects": float(rating.network_effects_score),
            "intangible_assets": float(rating.intangible_assets_score),
            "cost_advantages": float(rating.cost_advantages_score),
            "switching_costs": float(rating.switching_costs_score),
            "efficient_scale": float(rating.efficient_scale_score),
        },
        "trajectory": rating.trajectory,
        "calculated_at": rating.calculated_at.isoformat(),
    }


@router.get("/ts-score/{ticker}", response_model=TSScoreResponse)
async def get_ts_score(
    ticker: str,
    current_user: User = Depends(require_feature("research_api", "Research API access")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get TradeSignal Score for a stock.

    Requires Research Pro or Enterprise tier.
    """
    await _check_research_api_limit(current_user, db)

    ts_service = TSScoreService(db)
    score = await ts_service.get_latest_ts_score(ticker)

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TS Score not found for {ticker}",
        )

    await TierService.increment_api_usage(current_user.id, db)

    return {
        "ticker": ticker,
        "ts_score": float(score.score),
        "badge": score.badge,
        "components": {
            "insider_buy_ratio": float(score.insider_buy_ratio),
            "ivt_discount_premium": float(score.ivt_discount_premium),
            "risk_score": float(score.risk_score),
            "politician_score": float(score.politician_score),
        },
        "calculated_at": score.calculated_at.isoformat(),
    }


@router.get("/comprehensive/{ticker}", response_model=ComprehensiveResearchResponse)
async def get_comprehensive_research(
    ticker: str,
    current_user: User = Depends(require_feature("research_api", "Research API access")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive research data for a stock.

    Includes IVT, Risk Level, TS Score, and optionally Management Score and Competitive Strength.
    Requires Enterprise tier for full data.

    Returns all available research metrics based on user tier.
    """
    await _check_research_api_limit(current_user, db)

    tier = await TierService.get_user_tier(current_user.id, db)
    is_enterprise = tier == SubscriptionTier.ENTERPRISE.value

    # Get all available data
    dcf_service = DCFService(db)
    risk_service = RiskLevelService(db)
    ts_service = TSScoreService(db)

    ivt = await dcf_service.get_latest_ivt(ticker)
    risk = await risk_service.get_latest_risk_level(ticker)
    ts_score = await ts_service.get_latest_ts_score(ticker)

    result = {
        "ticker": ticker,
        "ivt": {
            "intrinsic_value": float(ivt.intrinsic_value) if ivt else None,
            "current_price": float(ivt.current_price) if ivt else None,
            "discount_premium_pct": float(ivt.discount_premium_pct) if ivt else None,
        } if ivt else None,
        "risk_level": {
            "risk_level": risk.risk_level,
            "score": float(risk.score),
        } if risk else None,
        "ts_score": {
            "score": float(ts_score.score),
            "badge": ts_score.badge,
        } if ts_score else None,
    }

    # Enterprise-only features
    if is_enterprise:
        management_service = ManagementScoreService(db)
        strength_service = CompetitiveStrengthService(db)

        management = await management_service.get_latest_score(ticker)
        strength = await strength_service.get_latest_rating(ticker)

        result["management_score"] = {
            "grade": management.grade,
            "composite_score": float(management.composite_score),
        } if management else None

        result["competitive_strength"] = {
            "rating": strength.rating,
            "composite_score": float(strength.composite_score),
            "trajectory": strength.trajectory,
        } if strength else None

    await TierService.increment_api_usage(current_user.id, db)

    return result


@router.get("/usage")
async def get_research_api_usage(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get Research API usage statistics.

    Shows current usage and limits.
    """
    tier = await TierService.get_user_tier(current_user.id, db)
    limits = RESEARCH_API_TIERS.get(tier, RESEARCH_API_TIERS[SubscriptionTier.PRO.value])
    usage = await TierService.get_or_create_usage(current_user.id, db)

    monthly_limit = limits["requests_per_month"]
    available_features = limits["features"]

    return {
        "tier": tier,
        "monthly_limit": monthly_limit if monthly_limit != -1 else "unlimited",
        "requests_this_month": usage.api_calls,  # Would track separately for research API
        "remaining": (
            monthly_limit - usage.api_calls if monthly_limit != -1 else "unlimited"
        ),
        "available_features": available_features,
        "reset_at": (datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat(),
    }


async def _check_research_api_limit(
    current_user: User, db: AsyncSession
) -> None:
    """Check if user has exceeded Research API rate limit."""
    tier = await TierService.get_user_tier(current_user.id, db)
    limits = RESEARCH_API_TIERS.get(tier, RESEARCH_API_TIERS[SubscriptionTier.PRO.value])

    monthly_limit = limits["requests_per_month"]
    if monthly_limit == -1:
        return  # Unlimited

    usage = await TierService.get_or_create_usage(current_user.id, db)
    if usage.api_calls >= monthly_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Research API rate limit exceeded. Limit: {monthly_limit} requests/month. Upgrade for higher limits.",
        )

