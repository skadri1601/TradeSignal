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
from datetime import datetime
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
from app.services.cache_service import cache_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


def require_pro_tier(current_user: User = Depends(get_current_active_user)):
    """
    Dependency to require PRO tier or higher for research features.

    PORTFOLIO MODE: All features are free - tier check bypassed.
    """
    # PORTFOLIO MODE: Skip tier checks - all features are free
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
            .where(IntrinsicValueTarget.ticker == ticker)
            .order_by(IntrinsicValueTarget.calculated_at.desc())
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
                "calculation_date": ivt.calculated_at.isoformat(),
                "confidence_score": None,  # Model doesn't have this field
                "wacc": float(ivt.wacc) if ivt.wacc else None,
                "terminal_growth_rate": float(ivt.terminal_growth_rate) if ivt.terminal_growth_rate else None,
                "cached": True
            }

        # If not cached, calculate on-demand
        from app.services.ivt_data_service import IVTDataService

        ivt_service = IVTDataService(db)
        ivt_data = await ivt_service.calculate_ivt_for_company(ticker)

        if not ivt_data:
            raise HTTPException(
                status_code=404,
                detail=f"Unable to calculate IVT for {ticker}. Company data may not be available."
            )

        # Return freshly calculated IVT
        return {
            "ticker": ticker,
            "intrinsic_value": ivt_data["intrinsic_value"],
            "current_price": ivt_data["current_price"],
            "discount_pct": ivt_data["discount_premium_pct"],
            "calculation_date": datetime.utcnow().isoformat(),
            "confidence_score": None,
            "wacc": ivt_data.get("wacc"),
            "terminal_growth_rate": ivt_data.get("terminal_growth_rate"),
            "cached": False
        }

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
    Calculates on-the-fly if data doesn't exist.
    """
    ticker = ticker.upper()

    try:
        # Check if TS Score exists in database
        result = await db.execute(
            select(TradeSignalScore)
            .where(TradeSignalScore.ticker == ticker)
            .order_by(TradeSignalScore.calculated_at.desc())
            .limit(1)
        )
        ts_score = result.scalar_one_or_none()

        if ts_score:
            # Use rating from model if available, otherwise map from score
            rating_map = {
                5: "Strong Buy",
                4: "Buy",
                3: "Hold",
                2: "Sell",
                1: "Strong Sell"
            }

            score_value = float(ts_score.score) if ts_score.score else 3.0
            rating_text = ts_score.rating or rating_map.get(round(score_value), "Hold")

            return {
                "ticker": ticker,
                "score": score_value,
                "rating": rating_text,
                "price_to_ivt_ratio": float(ts_score.p_ivt_ratio) if ts_score.p_ivt_ratio else None,
                "risk_adjusted": ts_score.risk_level is not None,
                "calculation_date": ts_score.calculated_at.isoformat() if ts_score.calculated_at else None,
                "cached": True,
                "cache_source": "database"
            }

        # Calculate on-demand if not cached
        logger.info(f"Calculating TS Score for {ticker} on-the-fly")
        ts_service = TSScoreService(db)

        try:
            calculation_result = await ts_service.calculate_ts_score(ticker)
        except ValueError as e:
            logger.warning(f"Cannot calculate TS Score for {ticker}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Cannot calculate TS Score for {ticker}: {str(e)}"
            )

        # Save to database
        await ts_service.save_ts_score(calculation_result)

        # Map badge to rating
        badge_to_rating = {
            "excellent": "Strong Buy",
            "strong": "Buy",
            "good": "Buy",
            "moderate": "Hold",
            "weak": "Sell",
            "poor": "Strong Sell"
        }

        return {
            "ticker": ticker,
            "score": calculation_result["ts_score"],
            "rating": badge_to_rating.get(calculation_result["badge"], "Hold"),
            "price_to_ivt_ratio": calculation_result["components"].get("ivt_discount_premium"),
            "risk_adjusted": True,
            "calculation_date": calculation_result["calculated_at"],
            "cached": False,
            "cache_source": "calculated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching TS Score for {ticker}: {e}", exc_info=True)
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
    Calculates on-the-fly if data doesn't exist.
    """
    ticker = ticker.upper()

    try:
        # Check if risk assessment exists
        result = await db.execute(
            select(RiskLevelAssessment)
            .where(RiskLevelAssessment.ticker == ticker)
            .order_by(RiskLevelAssessment.calculated_at.desc())
            .limit(1)
        )
        risk = result.scalar_one_or_none()

        if risk:
            return {
                "ticker": ticker,
                "level": risk.risk_level,
                "category": risk.risk_level,
                "volatility_score": float(risk.earnings_volatility_score) if risk.earnings_volatility_score else None,
                "assessment_date": risk.calculated_at.isoformat() if risk.calculated_at else None,
                "components": {
                    "earnings_volatility": float(risk.earnings_volatility_score) if risk.earnings_volatility_score else None,
                    "financial_leverage": float(risk.financial_leverage_score) if risk.financial_leverage_score else None,
                    "operating_leverage": float(risk.operating_leverage_score) if risk.operating_leverage_score else None,
                    "concentration_risk": float(risk.concentration_score) if risk.concentration_score else None,
                    "industry_stability": float(risk.industry_stability_score) if risk.industry_stability_score else None
                },
                "cached": True,
                "cache_source": "database"
            }

        # Calculate on-demand if not cached
        logger.info(f"Calculating Risk Level for {ticker} on-the-fly")
        risk_service = RiskLevelService(db)

        # Calculate with defaults (service handles missing data gracefully)
        calculation_result = await risk_service.calculate_risk_level(ticker)

        # Save to database
        await risk_service.save_risk_assessment(calculation_result)

        return {
            "ticker": ticker,
            "level": calculation_result["risk_level"],
            "category": calculation_result["risk_level"],
            "volatility_score": calculation_result["component_scores"]["earnings_volatility"],
            "assessment_date": calculation_result["calculated_at"],
            "components": {
                "earnings_volatility": calculation_result["component_scores"]["earnings_volatility"],
                "financial_leverage": calculation_result["component_scores"]["financial_leverage"],
                "operating_leverage": calculation_result["component_scores"]["operating_leverage"],
                "concentration_risk": calculation_result["component_scores"]["concentration"],
                "industry_stability": calculation_result["component_scores"]["industry_stability"]
            },
            "cached": False,
            "cache_source": "calculated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Risk Level for {ticker}: {e}", exc_info=True)
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
    Calculates on-the-fly if data doesn't exist.
    """
    ticker = ticker.upper()

    try:
        from app.services.competitive_strength_service import CompetitiveStrengthService
        from app.models.competitive_strength import CompetitiveStrengthRating
        from datetime import datetime

        # Check Redis cache first
        cache_key = f"competitive_strength:{ticker}:latest"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for competitive strength: {ticker}")
            cached_result["cached"] = True
            cached_result["cache_source"] = "redis"
            return cached_result

        # Check database
        result = await db.execute(
            select(CompetitiveStrengthRating)
            .where(CompetitiveStrengthRating.ticker == ticker)
            .order_by(CompetitiveStrengthRating.calculated_at.desc())
            .limit(1)
        )
        comp = result.scalar_one_or_none()

        if comp:
            response_data = {
                "ticker": ticker,
                "rating": comp.rating,
                "trajectory": comp.trajectory,
                "composite_score": float(comp.composite_score) if comp.composite_score else None,
                "moat_sources": {
                    "network_effects": float(comp.network_effects_score) if comp.network_effects_score else None,
                    "intangible_assets": float(comp.intangible_assets_score) if comp.intangible_assets_score else None,
                    "cost_advantages": float(comp.cost_advantages_score) if comp.cost_advantages_score else None,
                    "switching_costs": float(comp.switching_costs_score) if comp.switching_costs_score else None,
                    "efficient_scale": float(comp.efficient_scale_score) if comp.efficient_scale_score else None
                },
                "rating_date": comp.calculated_at.isoformat() if comp.calculated_at else None,
                "cached": True,
                "cache_source": "database"
            }
            # Cache the result
            await cache_service.set(cache_key, response_data, ttl=settings.cache_competitive_strength_ttl)
            return response_data

        # Calculate on-the-fly if not cached
        logger.info(f"Calculating competitive strength for {ticker} on-the-fly")
        strength_service = CompetitiveStrengthService(db)
        
        try:
            # Calculate with real financial data (will fetch automatically if not provided)
            calculation_result = await strength_service.calculate_competitive_strength(ticker=ticker)
        except ValueError as e:
            # Financial data unavailable - return error instead of dummy data
            logger.error(f"Cannot calculate competitive strength for {ticker}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Financial data unavailable for {ticker}. Please ensure Financial Modeling Prep API is configured and try again later."
            )

        # Save to database
        comp_rating = CompetitiveStrengthRating(
            ticker=ticker,
            rating=calculation_result["rating"],
            composite_score=calculation_result["composite_score"],
            network_effects_score=calculation_result["component_scores"]["network_effects"],
            intangible_assets_score=calculation_result["component_scores"]["intangible_assets"],
            cost_advantages_score=calculation_result["component_scores"]["cost_advantages"],
            switching_costs_score=calculation_result["component_scores"]["switching_costs"],
            efficient_scale_score=calculation_result["component_scores"]["efficient_scale"],
            trajectory=calculation_result["trajectory"],
            calculated_at=datetime.utcnow(),
        )
        db.add(comp_rating)
        await db.commit()
        await db.refresh(comp_rating)

        response_data = {
            "ticker": ticker,
            "rating": comp_rating.rating,
            "trajectory": comp_rating.trajectory,
            "composite_score": float(comp_rating.composite_score),
            "moat_sources": {
                "network_effects": float(comp_rating.network_effects_score),
                "intangible_assets": float(comp_rating.intangible_assets_score),
                "cost_advantages": float(comp_rating.cost_advantages_score),
                "switching_costs": float(comp_rating.switching_costs_score),
                "efficient_scale": float(comp_rating.efficient_scale_score)
            },
            "rating_date": comp_rating.calculated_at.isoformat(),
            "cached": False,
            "cache_source": "calculated"
        }
        
        # Cache the newly calculated result
        await cache_service.set(cache_key, response_data, ttl=settings.cache_competitive_strength_ttl)
        
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Competitive Strength for {ticker}: {e}", exc_info=True)
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
    Calculates on-the-fly if data doesn't exist.
    """
    ticker = ticker.upper()

    try:
        from app.services.management_score_service import ManagementScoreService
        from app.models.management_score import ManagementScore
        from datetime import datetime

        # Check Redis cache first
        cache_key = f"management_score:{ticker}:latest"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for management score: {ticker}")
            cached_result["cached"] = True
            cached_result["cache_source"] = "redis"
            return cached_result

        # Check database
        result = await db.execute(
            select(ManagementScore)
            .where(ManagementScore.ticker == ticker)
            .order_by(ManagementScore.calculated_at.desc())
            .limit(1)
        )
        mgmt = result.scalar_one_or_none()

        if mgmt:
            response_data = {
                "ticker": ticker,
                "grade": mgmt.grade,
                "composite_score": float(mgmt.composite_score) if mgmt.composite_score else None,
                "components": {
                    "ma_track_record": float(mgmt.m_and_a_score) if mgmt.m_and_a_score else None,
                    "capital_discipline": float(mgmt.capital_discipline_score) if mgmt.capital_discipline_score else None,
                    "shareholder_returns": float(mgmt.shareholder_returns_score) if mgmt.shareholder_returns_score else None,
                    "financial_leverage": float(mgmt.leverage_management_score) if mgmt.leverage_management_score else None,
                    "governance": float(mgmt.governance_score) if mgmt.governance_score else None
                },
                "scoring_date": mgmt.calculated_at.isoformat() if mgmt.calculated_at else None,
                "cached": True,
                "cache_source": "database"
            }
            # Cache the result
            await cache_service.set(cache_key, response_data, ttl=settings.cache_management_score_ttl)
            return response_data

        # Calculate on-the-fly if not cached
        logger.info(f"Calculating management score for {ticker} on-the-fly")
        management_service = ManagementScoreService(db)
        
        try:
            # Calculate with real financial data, M&A history, and insider patterns
            calculation_result = await management_service.calculate_management_score(ticker=ticker)
        except ValueError as e:
            # Financial data or M&A data unavailable - return error instead of dummy data
            logger.error(f"Cannot calculate management score for {ticker}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Financial data or M&A data unavailable for {ticker}. Please ensure Financial Modeling Prep API is configured and try again later."
            )

        # Save to database
        mgmt_score = ManagementScore(
            ticker=ticker,
            grade=calculation_result["grade"],
            composite_score=calculation_result["composite_score"],
            m_and_a_score=calculation_result["component_scores"]["m_and_a"],
            capital_discipline_score=calculation_result["component_scores"]["capital_discipline"],
            shareholder_returns_score=calculation_result["component_scores"]["shareholder_returns"],
            leverage_management_score=calculation_result["component_scores"]["leverage_management"],
            governance_score=calculation_result["component_scores"]["governance"],
            calculated_at=datetime.utcnow(),
        )
        db.add(mgmt_score)
        await db.commit()
        await db.refresh(mgmt_score)

        response_data = {
            "ticker": ticker,
            "grade": mgmt_score.grade,
            "composite_score": float(mgmt_score.composite_score),
            "components": {
                "ma_track_record": float(mgmt_score.m_and_a_score),
                "capital_discipline": float(mgmt_score.capital_discipline_score),
                "shareholder_returns": float(mgmt_score.shareholder_returns_score),
                "financial_leverage": float(mgmt_score.leverage_management_score),
                "governance": float(mgmt_score.governance_score)
            },
            "scoring_date": mgmt_score.calculated_at.isoformat(),
            "cached": False,
            "cache_source": "calculated"
        }
        
        # Cache the newly calculated result
        await cache_service.set(cache_key, response_data, ttl=settings.cache_management_score_ttl)
        
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Management Score for {ticker}: {e}", exc_info=True)
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
        # Get tickers with IVT coverage (query ticker directly from model)
        ivt_result = await db.execute(
            select(IntrinsicValueTarget.ticker).distinct()
        )
        ivt_tickers = set([row[0] for row in ivt_result.all()])

        # Get tickers with TS Score coverage (query ticker directly from model)
        ts_result = await db.execute(
            select(TradeSignalScore.ticker).distinct()
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
