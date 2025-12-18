"""
TradeSignal Score Implementation Service.

Risk-adjusted thresholds, real-time updates, politician trade integration.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.tradesignal_score import TradeSignalScore
from app.models.company import Company
from app.models.trade import Trade
from app.models.risk_level import RiskLevelAssessment
from app.models.intrinsic_value import IntrinsicValueTarget
from app.services.risk_level_service import RiskLevelService
from app.services.dcf_service import DCFService

logger = logging.getLogger(__name__)


class TSScoreService:
    """Service for calculating and managing TradeSignal Scores."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.risk_service = RiskLevelService(db)
        self.dcf_service = DCFService(db)

    async def calculate_ts_score(
        self, ticker: str, include_politician_trades: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate TradeSignal Score for a company.

        Integrates:
        - Risk level assessment
        - Intrinsic value target
        - Politician trade activity
        - Insider trading patterns
        """
        # Get company
        result = await self.db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        company = result.scalar_one_or_none()

        if not company:
            raise ValueError(f"Company {ticker} not found")

        # Get latest risk level
        risk_assessment = await self.risk_service.get_latest_risk_level(ticker)
        risk_score = risk_assessment.score if risk_assessment else 50.0
        risk_level = risk_assessment.risk_level if risk_assessment else "moderate"

        # Get latest IVT
        ivt_result = await self.dcf_service.get_latest_ivt(ticker)
        ivt_value = ivt_result.intrinsic_value if ivt_result else None
        discount_premium = ivt_result.discount_premium_pct if ivt_result else 0.0

        # Get recent insider activity (last 90 days)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        result = await self.db.execute(
            select(
                func.count(Trade.id).label("trade_count"),
                func.sum(
                    func.case((Trade.transaction_type == "BUY", Trade.total_value), else_=0)
                ).label("buy_value"),
                func.sum(
                    func.case((Trade.transaction_type == "SELL", Trade.total_value), else_=0)
                ).label("sell_value"),
            )
            .join(Company, Trade.company_id == Company.id)
            .where(
                Company.ticker == ticker.upper(),
                Trade.filing_date >= cutoff_date,
            )
        )
        trade_stats = result.first()

        buy_value = float(trade_stats.buy_value or 0)
        sell_value = float(trade_stats.sell_value or 0)
        total_value = buy_value + sell_value
        buy_ratio = (buy_value / total_value * 100) if total_value > 0 else 50.0

        # Get politician trade activity if enabled
        politician_score = 0.0
        if include_politician_trades:
            politician_score = await self._calculate_politician_trade_score(ticker)

        # Calculate composite TS Score (0-100)
        # Components:
        # - Insider buy ratio (40%)
        # - IVT discount/premium (30%)
        # - Risk level (20%)
        # - Politician trades (10%)

        # Normalize buy ratio to 0-100 score
        buy_ratio_score = buy_ratio  # Already 0-100

        # Normalize discount/premium to 0-100 score
        # Positive discount (undervalued) = higher score
        # Negative premium (overvalued) = lower score
        ivt_score = 50.0 + (discount_premium * 0.5)  # Scale discount to score
        ivt_score = max(0.0, min(100.0, ivt_score))

        # Invert risk score (lower risk = higher score)
        risk_score_normalized = 100.0 - risk_score

        # Calculate composite
        ts_score = (
            buy_ratio_score * 0.40
            + ivt_score * 0.30
            + risk_score_normalized * 0.20
            + politician_score * 0.10
        )

        # Determine badge/threshold
        badge = self._determine_badge(ts_score)

        return {
            "ticker": ticker,
            "ts_score": round(ts_score, 2),
            "badge": badge,
            "components": {
                "insider_buy_ratio": round(buy_ratio, 2),
                "ivt_discount_premium": round(discount_premium, 2),
                "risk_score": round(risk_score, 2),
                "politician_score": round(politician_score, 2),
            },
            "calculated_at": datetime.utcnow().isoformat(),
        }

    async def _calculate_politician_trade_score(self, ticker: str) -> float:
        """
        Calculate score based on politician trade activity.

        Returns 0-100 score.
        """
        from app.models.congressional_trade import CongressionalTrade

        # Get recent politician trades (last 90 days)
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        result = await self.db.execute(
            select(
                func.count(CongressionalTrade.id).label("trade_count"),
                func.sum(
                    func.case(
                        (CongressionalTrade.transaction_type == "BUY", CongressionalTrade.total_value),
                        else_=0,
                    )
                ).label("buy_value"),
            )
            .join(Company, CongressionalTrade.company_id == Company.id)
            .where(
                Company.ticker == ticker.upper(),
                CongressionalTrade.filing_date >= cutoff_date,
            )
        )
        stats = result.first()

        trade_count = stats.trade_count or 0
        buy_value = float(stats.buy_value or 0)

        # Score based on activity
        if trade_count == 0:
            return 50.0  # Neutral

        # Higher buy value = higher score
        # Normalize to 0-100 (assuming max $10M in politician trades)
        score = min(100.0, (buy_value / 10000000) * 100)
        return score

    def _determine_badge(self, ts_score: float) -> str:
        """Determine badge based on TS Score."""
        if ts_score >= 80:
            return "excellent"
        elif ts_score >= 70:
            return "strong"
        elif ts_score >= 60:
            return "good"
        elif ts_score >= 50:
            return "moderate"
        elif ts_score >= 40:
            return "weak"
        else:
            return "poor"

    async def save_ts_score(self, score_data: Dict[str, Any]) -> TradeSignalScore:
        """Save TS Score to database."""
        score = TradeSignalScore(
            ticker=score_data["ticker"].upper(),
            score=score_data["ts_score"],
            badge=score_data["badge"],
            insider_buy_ratio=score_data["components"]["insider_buy_ratio"],
            ivt_discount_premium=score_data["components"]["ivt_discount_premium"],
            risk_score=score_data["components"]["risk_score"],
            politician_score=score_data["components"]["politician_score"],
            calculated_at=datetime.fromisoformat(score_data["calculated_at"]),
        )

        self.db.add(score)
        await self.db.commit()
        await self.db.refresh(score)

        return score

    async def get_latest_ts_score(self, ticker: str) -> Optional[TradeSignalScore]:
        """Get the latest TS Score for a ticker."""
        result = await self.db.execute(
            select(TradeSignalScore)
            .where(TradeSignalScore.ticker == ticker.upper())
            .order_by(TradeSignalScore.calculated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

