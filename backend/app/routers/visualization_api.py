"""
Visualization API Router.

Endpoints for data aggregation and formatting for frontend visualizations.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.trade import Trade
from app.models.company import Company
from app.models.intrinsic_value import IntrinsicValueTarget
from app.models.tradesignal_score import TradeSignalScore
from app.models.risk_level import RiskLevelAssessment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visualizations", tags=["Visualizations"])


@router.get("/trades/timeline/{ticker}")
async def get_trades_timeline(
    ticker: str,
    days_back: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get trades timeline data for visualization.

    Returns aggregated trade data over time for charting.
    """
    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Get company
    result = await db.execute(
        select(Company).where(Company.ticker == ticker.upper())
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {ticker} not found"
        )

    # Get trades grouped by date
    result = await db.execute(
        select(
            func.date(Trade.filing_date).label("date"),
            func.count(Trade.id).label("count"),
            func.sum(Trade.total_value).label("total_value"),
            func.avg(Trade.price_per_share).label("avg_price"),
        )
        .join(Company)
        .where(
            and_(
                Company.ticker == ticker.upper(),
                Trade.filing_date >= start_date,
            )
        )
        .group_by(func.date(Trade.filing_date))
        .order_by(func.date(Trade.filing_date))
    )
    timeline_data = result.fetchall()

    # Format for frontend
    timeline = [
        {
            "date": row.date.isoformat(),
            "count": row.count,
            "total_value": float(row.total_value or 0),
            "avg_price": float(row.avg_price or 0),
        }
        for row in timeline_data
    ]

    return {
        "ticker": ticker.upper(),
        "company_name": company.name,
        "timeline": timeline,
        "period": {
            "start": start_date.isoformat(),
            "end": datetime.utcnow().isoformat(),
            "days": days_back,
        },
    }


@router.get("/ivt/history/{ticker}")
async def get_ivt_history(
    ticker: str,
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get IVT calculation history for a ticker.

    Returns historical IVT values for price vs. IVT chart.
    """
    result = await db.execute(
        select(IntrinsicValueTarget)
        .where(IntrinsicValueTarget.ticker == ticker.upper())
        .order_by(IntrinsicValueTarget.calculated_at.desc())
        .limit(limit)
    )
    ivt_history = result.scalars().all()

    if not ivt_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVT history not found for {ticker}"
        )

    # Format for frontend chart
    history = [
        {
            "date": ivt.calculated_at.isoformat(),
            "intrinsic_value": float(ivt.intrinsic_value),
            "current_price": float(ivt.current_price),
            "discount_premium_pct": float(ivt.discount_premium_pct),
        }
        for ivt in reversed(ivt_history)  # Reverse to show chronological order
    ]

    latest = ivt_history[0]

    return {
        "ticker": ticker.upper(),
        "history": history,
        "latest": {
            "intrinsic_value": float(latest.intrinsic_value),
            "current_price": float(latest.current_price),
            "discount_premium_pct": float(latest.discount_premium_pct),
            "calculated_at": latest.calculated_at.isoformat(),
        },
    }


@router.get("/scores/comparison")
async def get_scores_comparison(
    tickers: str = Query(..., description="Comma-separated list of tickers"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get scores comparison for multiple tickers.

    Returns TS Score, Risk Level, and IVT for comparison visualization.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    
    if len(ticker_list) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 tickers allowed for comparison"
        )

    comparison_data = []

    for ticker in ticker_list:
        # Get TS Score
        result = await db.execute(
            select(TradeSignalScore)
            .where(TradeSignalScore.ticker == ticker)
            .order_by(TradeSignalScore.calculated_at.desc())
            .limit(1)
        )
        ts_score = result.scalar_one_or_none()

        # Get Risk Level
        result = await db.execute(
            select(RiskLevelAssessment)
            .where(RiskLevelAssessment.ticker == ticker)
            .order_by(RiskLevelAssessment.calculated_at.desc())
            .limit(1)
        )
        risk_level = result.scalar_one_or_none()

        # Get IVT
        result = await db.execute(
            select(IntrinsicValueTarget)
            .where(IntrinsicValueTarget.ticker == ticker)
            .order_by(IntrinsicValueTarget.calculated_at.desc())
            .limit(1)
        )
        ivt = result.scalar_one_or_none()

        comparison_data.append({
            "ticker": ticker,
            "ts_score": {
                "score": float(ts_score.score) if ts_score else None,
                "badge": ts_score.badge if ts_score else None,
            } if ts_score else None,
            "risk_level": {
                "level": risk_level.risk_level if risk_level else None,
                "score": float(risk_level.score) if risk_level else None,
            } if risk_level else None,
            "ivt": {
                "intrinsic_value": float(ivt.intrinsic_value) if ivt else None,
                "current_price": float(ivt.current_price) if ivt else None,
                "discount_premium_pct": float(ivt.discount_premium_pct) if ivt else None,
            } if ivt else None,
        })

    return {
        "tickers": ticker_list,
        "comparison": comparison_data,
    }


@router.get("/portfolio/performance/{portfolio_id}")
async def get_portfolio_performance(
    portfolio_id: int,
    days_back: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get portfolio performance data for visualization.

    Returns portfolio value over time for performance charts.
    """
    from app.models.portfolio import PortfolioPerformance

    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Verify portfolio belongs to user
    from app.models.portfolio import VirtualPortfolio
    result = await db.execute(
        select(VirtualPortfolio).where(
            and_(
                VirtualPortfolio.id == portfolio_id,
                VirtualPortfolio.user_id == current_user.id,
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    # Get performance snapshots
    result = await db.execute(
        select(PortfolioPerformance)
        .where(
            and_(
                PortfolioPerformance.portfolio_id == portfolio_id,
                PortfolioPerformance.snapshot_date >= start_date,
            )
        )
        .order_by(PortfolioPerformance.snapshot_date)
    )
    performance_data = result.scalars().all()

    # Format for frontend
    performance = [
        {
            "date": perf.snapshot_date.isoformat(),
            "total_value": float(perf.total_value),
            "total_cost": float(perf.total_cost),
            "gain_loss": float(perf.gain_loss),
            "gain_loss_pct": float(perf.gain_loss_pct),
        }
        for perf in performance_data
    ]

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "performance": performance,
        "period": {
            "start": start_date.isoformat(),
            "end": datetime.utcnow().isoformat(),
            "days": days_back,
        },
    }

