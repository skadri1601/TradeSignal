"""
Research API Router

Provides endpoints for accessing research features:
- Intrinsic Value Target (IVT)
- TradeSignal Score (TS Score)
- Risk Level Assessment
- Competitive Strength Rating
- Management Excellence Score
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.company import Company
from app.models.intrinsic_value import IntrinsicValueTarget
from app.models.tradesignal_score import TradeSignalScore
from app.models.risk_level import RiskLevelAssessment
from app.models.competitive_strength import CompetitiveStrengthRating
from app.models.management_score import ManagementScore
from app.services.ts_score_service import TSScoreService
from app.services.risk_level_service import RiskLevelService
from app.services.dcf_service import DCFService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


def require_pro_tier(current_user: User = Depends(get_current_active_user)):
    """
    Dependency to require PRO tier or higher for research features.
    """
    allowed_tiers = ["pro", "enterprise"]
    if current_user.subscription_tier not in allowed_tiers:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Premium feature",
                "message": "Research features require PRO subscription",
                "required_tier": "pro",
                "current_tier": current_user.subscription_tier,
                "upgrade_url": "/pricing"
            }
        )
    return current_user


@router.get("/{ticker}/ivt")
async def get_intrinsic_value(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get Intrinsic Value Target (IVT) for a stock.

    Returns DCF-based fair value estimate.
    """
    ticker = ticker.upper()

    try:
        # Check if IVT exists in database
        result = await db.execute(
            select(IntrinsicValueTarget)
            .join(Company)
            .where(Company.ticker == ticker)
            .order_by(IntrinsicValueTarget.calculation_date.desc())
            .limit(1)
        )
        ivt = result.scalar_one_or_none()

        if ivt:
            # Return cached IVT
            return {
                "ticker": ticker,
                "intrinsic_value": float(ivt.intrinsic_value),
                "current_price": float(ivt.current_price),
                "discount_pct": float(ivt.discount_premium_pct),
                "calculation_date": ivt.calculation_date.isoformat(),
                "confidence_score": float(ivt.confidence_score) if ivt.confidence_score else None,
                "wacc": float(ivt.wacc) if ivt.wacc else None,
                "terminal_growth_rate": float(ivt.terminal_growth_rate) if ivt.terminal_growth_rate else None,
                "cached": True
            }

        # If not cached, calculate on-demand (for now, return not found)
        # TODO: Implement on-demand calculation via DCFService
        raise HTTPException(
            status_code=404,
            detail=f"Intrinsic Value Target not yet calculated for {ticker}. Coverage coming soon."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching IVT for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker}/ts-score")
async def get_ts_score(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get TradeSignal Score (1-5 rating) for a stock.

    Risk-adjusted valuation score combining IVT, risk level, and market factors.
    """
    ticker = ticker.upper()

    try:
        # Check if TS Score exists in database
        result = await db.execute(
            select(TradeSignalScore)
            .join(Company)
            .where(Company.ticker == ticker)
            .order_by(TradeSignalScore.calculation_date.desc())
            .limit(1)
        )
        ts_score = result.scalar_one_or_none()

        if ts_score:
            # Map numeric score to rating text
            rating_map = {
                5: "Strong Buy",
                4: "Buy",
                3: "Hold",
                2: "Sell",
                1: "Strong Sell"
            }

            score_value = float(ts_score.score)
            rating_text = rating_map.get(round(score_value), "Hold")

            return {
                "ticker": ticker,
                "score": score_value,
                "rating": rating_text,
                "price_to_ivt_ratio": float(ts_score.price_to_ivt_ratio) if ts_score.price_to_ivt_ratio else None,
                "risk_adjusted": ts_score.risk_adjusted_score is not None,
                "calculation_date": ts_score.calculation_date.isoformat() if ts_score.calculation_date else None,
                "cached": True
            }

        # If not cached, return placeholder
        raise HTTPException(
            status_code=404,
            detail=f"TradeSignal Score not yet calculated for {ticker}. Coverage coming soon."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching TS Score for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker}/risk-level")
async def get_risk_level(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get Risk Level Assessment for a stock.

    Returns risk category and component scores.
    """
    ticker = ticker.upper()

    try:
        # Check if risk assessment exists
        result = await db.execute(
            select(RiskLevelAssessment)
            .join(Company)
            .where(Company.ticker == ticker)
            .order_by(RiskLevelAssessment.assessment_date.desc())
            .limit(1)
        )
        risk = result.scalar_one_or_none()

        if risk:
            return {
                "ticker": ticker,
                "level": risk.risk_category,
                "category": risk.risk_category,
                "volatility_score": float(risk.earnings_volatility_score) if risk.earnings_volatility_score else None,
                "assessment_date": risk.assessment_date.isoformat() if risk.assessment_date else None,
                "components": {
                    "earnings_volatility": float(risk.earnings_volatility_score) if risk.earnings_volatility_score else None,
                    "financial_leverage": float(risk.financial_leverage_score) if risk.financial_leverage_score else None,
                    "operating_leverage": float(risk.operating_leverage_score) if risk.operating_leverage_score else None,
                    "concentration_risk": float(risk.concentration_risk_score) if risk.concentration_risk_score else None,
                    "industry_stability": float(risk.industry_stability_score) if risk.industry_stability_score else None
                },
                "cached": True
            }

        raise HTTPException(
            status_code=404,
            detail=f"Risk Level Assessment not yet available for {ticker}. Coverage coming soon."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Risk Level for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker}/competitive-strength")
async def get_competitive_strength(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get Competitive Strength Rating for a stock.

    Returns moat analysis and competitive advantage assessment.
    """
    ticker = ticker.upper()

    try:
        # Check if competitive strength rating exists
        result = await db.execute(
            select(CompetitiveStrengthRating)
            .join(Company)
            .where(Company.ticker == ticker)
            .order_by(CompetitiveStrengthRating.rating_date.desc())
            .limit(1)
        )
        comp = result.scalar_one_or_none()

        if comp:
            return {
                "ticker": ticker,
                "rating": comp.rating,
                "trajectory": comp.competitive_trajectory,
                "composite_score": float(comp.composite_score) if comp.composite_score else None,
                "moat_sources": {
                    "network_effects": float(comp.network_effects_score) if comp.network_effects_score else None,
                    "intangible_assets": float(comp.intangible_assets_score) if comp.intangible_assets_score else None,
                    "cost_advantages": float(comp.cost_advantages_score) if comp.cost_advantages_score else None,
                    "switching_costs": float(comp.switching_costs_score) if comp.switching_costs_score else None,
                    "efficient_scale": float(comp.efficient_scale_score) if comp.efficient_scale_score else None
                },
                "rating_date": comp.rating_date.isoformat() if comp.rating_date else None,
                "cached": True
            }

        raise HTTPException(
            status_code=404,
            detail=f"Competitive Strength Rating not yet available for {ticker}. Coverage coming soon."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Competitive Strength for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker}/management-score")
async def get_management_score(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get Management Excellence Score for a stock.

    Returns capital allocation and stewardship assessment.
    """
    ticker = ticker.upper()

    try:
        # Check if management score exists
        result = await db.execute(
            select(ManagementScore)
            .join(Company)
            .where(Company.ticker == ticker)
            .order_by(ManagementScore.scoring_date.desc())
            .limit(1)
        )
        mgmt = result.scalar_one_or_none()

        if mgmt:
            return {
                "ticker": ticker,
                "grade": mgmt.overall_grade,
                "composite_score": float(mgmt.composite_score) if mgmt.composite_score else None,
                "components": {
                    "ma_track_record": float(mgmt.ma_track_record_score) if mgmt.ma_track_record_score else None,
                    "capital_discipline": float(mgmt.capital_discipline_score) if mgmt.capital_discipline_score else None,
                    "shareholder_returns": float(mgmt.shareholder_returns_score) if mgmt.shareholder_returns_score else None,
                    "financial_leverage": float(mgmt.financial_leverage_score) if mgmt.financial_leverage_score else None,
                    "governance": float(mgmt.governance_score) if mgmt.governance_score else None
                },
                "scoring_date": mgmt.scoring_date.isoformat() if mgmt.scoring_date else None,
                "cached": True
            }

        raise HTTPException(
            status_code=404,
            detail=f"Management Excellence Score not yet available for {ticker}. Coverage coming soon."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Management Score for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker}/full-report")
async def get_full_research_report(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get comprehensive research report with all scores.

    Combines IVT, TS Score, Risk Level, Competitive Strength, and Management Score.
    """
    ticker = ticker.upper()

    try:
        # Fetch all research components
        report = {
            "ticker": ticker,
            "report_date": None,
            "ivt": None,
            "ts_score": None,
            "risk_level": None,
            "competitive_strength": None,
            "management_score": None
        }

        # Try to fetch each component
        try:
            ivt_response = await get_intrinsic_value(ticker, db, current_user)
            report["ivt"] = ivt_response
        except HTTPException:
            pass

        try:
            ts_response = await get_ts_score(ticker, db, current_user)
            report["ts_score"] = ts_response
        except HTTPException:
            pass

        try:
            risk_response = await get_risk_level(ticker, db, current_user)
            report["risk_level"] = risk_response
        except HTTPException:
            pass

        try:
            comp_response = await get_competitive_strength(ticker, db, current_user)
            report["competitive_strength"] = comp_response
        except HTTPException:
            pass

        try:
            mgmt_response = await get_management_score(ticker, db, current_user)
            report["management_score"] = mgmt_response
        except HTTPException:
            pass

        # Check if we got any data
        has_data = any([
            report["ivt"],
            report["ts_score"],
            report["risk_level"],
            report["competitive_strength"],
            report["management_score"]
        ])

        if not has_data:
            raise HTTPException(
                status_code=404,
                detail=f"No research data available for {ticker} yet. Coverage coming soon."
            )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating full report for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/coverage")
async def get_research_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pro_tier)
):
    """
    Get list of tickers with research coverage.

    Returns tickers that have at least one research component available.
    """
    try:
        # Get tickers with IVT coverage
        ivt_result = await db.execute(
            select(Company.ticker)
            .join(IntrinsicValueTarget)
            .distinct()
        )
        ivt_tickers = set([row[0] for row in ivt_result.all()])

        # Get tickers with TS Score coverage
        ts_result = await db.execute(
            select(Company.ticker)
            .join(TradeSignalScore)
            .distinct()
        )
        ts_tickers = set([row[0] for row in ts_result.all()])

        # Combine all covered tickers
        all_covered = list(ivt_tickers.union(ts_tickers))
        all_covered.sort()

        return {
            "total_coverage": len(all_covered),
            "tickers": all_covered,
            "coverage_types": {
                "ivt": len(ivt_tickers),
                "ts_score": len(ts_tickers)
            }
        }

    except Exception as e:
        logger.error(f"Error fetching research coverage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
