"""
Alert Prioritization Service

Implements intelligent noise filtering to show only 3-5% of significant trades
that actually have predictive value.

Filters based on:
- Trade value significance
- Insider role importance
- Pattern clustering
- Historical accuracy
- Market context
"""

import logging
from typing import List, Dict, Any
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models import Trade
# REMOVED: from app.services.pattern_analysis_service import PatternAnalysisService (service was deleted)
from app.services.trade_value_estimation_service import TradeValueEstimationService

logger = logging.getLogger(__name__)


class AlertPrioritizationService:
    """
    Service for filtering trades to only the most significant ones.

    Goal: Show only 3-5% of trades that have predictive value.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        # REMOVED: self.pattern_service = PatternAnalysisService(db) (unused, service was deleted)
        self.value_service = TradeValueEstimationService(db)

    async def filter_significant_trades(
        self, trades: List[Trade], target_percentage: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Filter trades to only the most significant ones.

        Args:
            trades: List of trades to filter
            target_percentage: Target percentage to keep (default: 5%)

        Returns:
            List of significant trades with scores
        """
        if not trades:
            return []

        # Score each trade
        scored_trades = []

        for trade in trades:
            score = await self._calculate_significance_score(trade)
            scored_trades.append(
                {
                    "trade": trade,
                    "score": score,
                    "is_significant": score >= 0.7,  # Threshold for significance
                }
            )

        # Sort by score
        scored_trades.sort(key=lambda x: x["score"], reverse=True)

        # Keep top percentage
        keep_count = max(1, int(len(trades) * target_percentage))
        significant = scored_trades[:keep_count]

        return [
            {
                "trade_id": item["trade"].id,
                "ticker": item["trade"].company.ticker
                if item["trade"].company
                else None,
                "insider": item["trade"].insider.name
                if item["trade"].insider
                else None,
                "score": item["score"],
                "reasons": await self._get_significance_reasons(
                    item["trade"], item["score"]
                ),
            }
            for item in significant
        ]

    async def _calculate_significance_score(self, trade: Trade) -> float:
        """
        Calculate significance score (0-1) for a trade.

        Factors:
        - Trade value (higher = more significant)
        - Insider role (CEO/CFO = more significant)
        - Pattern context (clustered = more significant)
        - Historical accuracy (if insider has good track record)
        """
        score = 0.0

        # Factor 1: Trade Value (40% weight)
        value_score = await self._calculate_value_score(trade)
        score += value_score * 0.4

        # Factor 2: Insider Role (25% weight)
        role_score = await self._calculate_role_score(trade)
        score += role_score * 0.25

        # Factor 3: Pattern Context (20% weight)
        pattern_score = await self._calculate_pattern_score(trade)
        score += pattern_score * 0.2

        # Factor 4: Historical Accuracy (15% weight)
        accuracy_score = await self._calculate_accuracy_score(trade)
        score += accuracy_score * 0.15

        return min(1.0, score)

    async def _calculate_value_score(self, trade: Trade) -> float:
        """Calculate score based on trade value."""
        # Get or estimate trade value
        if not trade.total_value or trade.total_value == 0:
            estimates = await self.value_service.estimate_missing_trade_value(trade)
            trade_value = estimates.get("total_value", 0)
        else:
            trade_value = float(trade.total_value)

        # Score based on value thresholds
        if trade_value >= 1_000_000:  # $1M+
            return 1.0
        elif trade_value >= 500_000:  # $500K+
            return 0.8
        elif trade_value >= 100_000:  # $100K+
            return 0.6
        elif trade_value >= 50_000:  # $50K+
            return 0.4
        elif trade_value >= 10_000:  # $10K+
            return 0.2
        else:
            return 0.1

    async def _calculate_role_score(self, trade: Trade) -> float:
        """Calculate score based on insider role."""
        if not trade.insider:
            return 0.3

        role = (trade.insider.title or trade.insider.relationship or "").upper()

        # C-suite executives
        if any(title in role for title in ["CEO", "CHIEF EXECUTIVE", "PRESIDENT"]):
            return 1.0
        elif any(title in role for title in ["CFO", "CHIEF FINANCIAL"]):
            return 0.9
        elif any(
            title in role
            for title in ["COO", "CHIEF OPERATING", "CTO", "CHIEF TECHNOLOGY"]
        ):
            return 0.8
        elif "DIRECTOR" in role:
            return 0.6
        elif "OFFICER" in role or "VP" in role or "VICE PRESIDENT" in role:
            return 0.5
        elif "10%" in role or "OWNER" in role:
            return 0.7
        else:
            return 0.3

    async def _calculate_pattern_score(self, trade: Trade) -> float:
        """Calculate score based on pattern context (clustering, timing)."""
        if not trade.company_id:
            return 0.3

        # Check for clustered activity (multiple insiders trading together)
        cutoff_date = trade.transaction_date - timedelta(days=7)

        result = await self.db.execute(
            select(func.count(Trade.id)).where(
                and_(
                    Trade.company_id == trade.company_id,
                    Trade.transaction_date >= cutoff_date,
                    Trade.transaction_date <= trade.transaction_date,
                    Trade.transaction_type == trade.transaction_type,
                )
            )
        )
        recent_count = result.scalar_one()

        # More clustered = higher score
        if recent_count >= 5:
            return 1.0
        elif recent_count >= 3:
            return 0.7
        elif recent_count >= 2:
            return 0.5
        else:
            return 0.3

    async def _calculate_accuracy_score(self, trade: Trade) -> float:
        """Calculate score based on insider's historical accuracy."""
        if not trade.insider_id or not trade.company_id:
            return 0.5

        # Get historical trades from this insider for this company
        cutoff_date = trade.transaction_date - timedelta(days=365)

        result = await self.db.execute(
            select(Trade)
            .where(
                and_(
                    Trade.insider_id == trade.insider_id,
                    Trade.company_id == trade.company_id,
                    Trade.transaction_date >= cutoff_date,
                    Trade.transaction_date < trade.transaction_date,
                )
            )
            .order_by(desc(Trade.transaction_date))
            .limit(10)
        )
        historical_trades = result.scalars().all()

        if len(historical_trades) < 3:
            return 0.5  # Not enough history

        # For now, return neutral score
        # In future, could track price movements after trades to calculate accuracy
        return 0.6

    async def _get_significance_reasons(self, trade: Trade, score: float) -> List[str]:
        """Get human-readable reasons why a trade is significant."""
        reasons = []

        # Value-based reasons
        if trade.total_value and trade.total_value >= 1_000_000:
            reasons.append("Large trade value ($1M+)")
        elif trade.total_value and trade.total_value >= 100_000:
            reasons.append("Significant trade value ($100K+)")

        # Role-based reasons
        if trade.insider:
            role = (trade.insider.title or trade.insider.relationship or "").upper()
            if "CEO" in role or "CHIEF EXECUTIVE" in role:
                reasons.append("CEO trade")
            elif "CFO" in role:
                reasons.append("CFO trade")
            elif "DIRECTOR" in role:
                reasons.append("Director trade")

        # Pattern-based reasons
        if score >= 0.8:
            reasons.append("High significance score")

        return reasons if reasons else ["Significant trade activity"]
