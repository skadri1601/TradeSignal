"""
Management Excellence Score Service.

Calculates A/B/C/D/F grade based on:
- M&A track record (30% weight)
- Capital discipline (25% weight)
- Shareholder returns (20% weight)
- Leverage management (15% weight)
- Governance (10% weight)

Unique differentiator: Cross-references with insider trading patterns.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.management_score import ManagementScore, ManagementGrade

logger = logging.getLogger(__name__)

# Component weights
WEIGHTS = {
    "m_and_a": 0.30,
    "capital_discipline": 0.25,
    "shareholder_returns": 0.20,
    "leverage_management": 0.15,
    "governance": 0.10,
}

# Grade thresholds
GRADE_THRESHOLDS = {
    ManagementGrade.A: (90, 100),
    ManagementGrade.B: (75, 90),
    ManagementGrade.C: (60, 75),
    ManagementGrade.D: (45, 60),
    ManagementGrade.F: (0, 45),
}


class ManagementScoreService:
    """Service for calculating management excellence scores."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_management_score(
        self,
        ticker: str,
        m_and_a_track_record: Optional[float] = None,  # 0-100 score
        capital_discipline: Optional[float] = None,  # 0-100 score
        shareholder_returns: Optional[float] = None,  # 0-100 score
        leverage_management: Optional[float] = None,  # 0-100 score
        governance: Optional[float] = None,  # 0-100 score
    ) -> Dict[str, Any]:
        """
        Calculate management excellence score.

        Args:
            ticker: Stock ticker symbol
            m_and_a_track_record: M&A track record score (0-100)
            capital_discipline: Capital discipline score (0-100)
            shareholder_returns: Shareholder returns score (0-100)
            leverage_management: Leverage management score (0-100)
            governance: Governance score (0-100)

        Returns:
            Dictionary with management score assessment
        """
        # Use defaults if not provided
        m_and_a = m_and_a_track_record if m_and_a_track_record is not None else 50.0
        capital = capital_discipline if capital_discipline is not None else 50.0
        returns = shareholder_returns if shareholder_returns is not None else 50.0
        leverage = leverage_management if leverage_management is not None else 50.0
        gov = governance if governance is not None else 50.0

        # Calculate weighted composite score
        composite_score = (
            m_and_a * WEIGHTS["m_and_a"]
            + capital * WEIGHTS["capital_discipline"]
            + returns * WEIGHTS["shareholder_returns"]
            + leverage * WEIGHTS["leverage_management"]
            + gov * WEIGHTS["governance"]
        )

        # Determine grade
        grade = self._determine_grade(composite_score)

        # Cross-reference with insider trading patterns (unique differentiator)
        insider_insights = await self._analyze_insider_trading_patterns(ticker)

        return {
            "ticker": ticker,
            "grade": grade.value,
            "composite_score": round(composite_score, 2),
            "component_scores": {
                "m_and_a": round(m_and_a, 2),
                "capital_discipline": round(capital, 2),
                "shareholder_returns": round(returns, 2),
                "leverage_management": round(leverage, 2),
                "governance": round(gov, 2),
            },
            "insider_insights": insider_insights,
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def _determine_grade(self, composite_score: float) -> ManagementGrade:
        """Determine grade from composite score."""
        for grade, (min_score, max_score) in GRADE_THRESHOLDS.items():
            if min_score <= composite_score < max_score:
                return grade
        # Default to F if score < 0
        return ManagementGrade.F

    async def _analyze_insider_trading_patterns(
        self, ticker: str
    ) -> Dict[str, Any]:
        """
        Analyze insider trading patterns for management score insights.

        Unique differentiator: Cross-reference management actions with insider trades.
        """
        from app.models.trade import Trade
        from app.models.company import Company
        from app.models.insider import Insider
        from datetime import timedelta

        try:
            # Get recent insider trades (last 2 years)
            cutoff_date = datetime.utcnow() - timedelta(days=730)

            result = await self.db.execute(
                select(Trade, Insider)
                .join(Company, Trade.company_id == Company.id)
                .join(Insider, Trade.insider_id == Insider.id)
                .where(
                    Company.ticker == ticker.upper(),
                    Trade.filing_date >= cutoff_date,
                )
                .order_by(Trade.filing_date.desc())
            )
            trades = result.all()

            if not trades:
                return {
                    "insider_activity": "No recent insider trading activity",
                    "pattern": "neutral",
                }

            # Analyze patterns
            buy_count = sum(1 for t, _ in trades if t.transaction_type == "BUY")
            sell_count = sum(1 for t, _ in trades if t.transaction_type == "SELL")
            total_count = len(trades)

            buy_ratio = buy_count / total_count if total_count > 0 else 0

            # Determine pattern
            if buy_ratio > 0.7:
                pattern = "management_buying"
                insight = "Management showing strong conviction through buying activity"
            elif buy_ratio < 0.3:
                pattern = "management_selling"
                insight = "Management selling activity may indicate concerns"
            else:
                pattern = "neutral"
                insight = "Mixed insider trading activity"

            return {
                "insider_activity": f"{buy_count} buys, {sell_count} sells in last 2 years",
                "pattern": pattern,
                "insight": insight,
                "buy_ratio": round(buy_ratio, 2),
            }

        except Exception as e:
            logger.error(f"Error analyzing insider patterns for {ticker}: {e}")
            return {
                "insider_activity": "Analysis unavailable",
                "pattern": "unknown",
            }

    async def get_latest_score(self, ticker: str) -> Optional[ManagementScore]:
        """Get the latest management score for a ticker."""
        result = await self.db.execute(
            select(ManagementScore)
            .where(ManagementScore.ticker == ticker.upper())
            .order_by(ManagementScore.calculated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

