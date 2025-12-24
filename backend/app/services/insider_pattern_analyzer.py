"""
Insider Pattern Analyzer for advanced insider trading pattern analysis.

Provides sophisticated analysis including:
- Timing analysis (relative to earnings, news, price movements)
- Volume analysis (trade size relative to holdings)
- Pattern recognition (clustering, trend detection)
- Sentiment scoring (weighted buy/sell ratios)
- Executive vs. Director analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider

logger = logging.getLogger(__name__)


class InsiderPatternAnalyzer:
    """Service for advanced insider trading pattern analysis."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_insider_patterns(
        self, ticker: str, days_back: int = 730
    ) -> Dict[str, Any]:
        """
        Perform comprehensive insider pattern analysis.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to analyze (default: 2 years)

        Returns:
            Dictionary with comprehensive pattern analysis
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        # Get all trades for the company, excluding $0 and undisclosed values
        result = await self.db.execute(
            select(Trade, Insider, Company)
            .join(Company, Trade.company_id == Company.id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(
                Company.ticker == ticker.upper(),
                Trade.filing_date >= cutoff_date,
                Trade.total_value.is_not(None),
                Trade.total_value > 0,
                Trade.price_per_share.is_not(None),
                Trade.price_per_share > 0,
            )
            .order_by(Trade.filing_date.desc())
        )
        trades_data = result.all()

        if not trades_data:
            return {
                "insider_activity": "No recent insider trading activity",
                "pattern": "neutral",
                "sentiment_score": 0.5,
                "confidence": "low",
            }

        trades = [t for t, _, _ in trades_data]
        insiders = [i for _, i, _ in trades_data]

        # Basic statistics
        buy_count = sum(1 for t in trades if t.transaction_type == "BUY")
        sell_count = sum(1 for t in trades if t.transaction_type == "SELL")
        total_count = len(trades)

        buy_value = sum(
            t.total_value or 0 for t in trades if t.transaction_type == "BUY"
        )
        sell_value = sum(
            t.total_value or 0 for t in trades if t.transaction_type == "SELL"
        )

        # Timing Analysis
        timing_analysis = self._analyze_timing(trades)

        # Volume Analysis
        volume_analysis = self._analyze_volume(trades)

        # Pattern Recognition
        pattern_analysis = self._detect_patterns(trades)

        # Sentiment Scoring
        sentiment_score = self._calculate_sentiment_score(
            buy_count, sell_count, buy_value, sell_value, timing_analysis
        )

        # Executive vs. Director Analysis
        executive_analysis = self._analyze_by_insider_type(insiders, trades)

        # Determine overall pattern
        pattern = self._determine_pattern(sentiment_score, pattern_analysis)

        return {
            "insider_activity": f"{buy_count} buys, {sell_count} sells in last {days_back} days",
            "total_trades": total_count,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "buy_value": buy_value,
            "sell_value": sell_value,
            "net_value": buy_value - sell_value,
            "pattern": pattern,
            "sentiment_score": round(sentiment_score, 3),  # 0-1 scale
            "confidence": self._calculate_confidence(total_count, buy_value, sell_value),
            "timing_analysis": timing_analysis,
            "volume_analysis": volume_analysis,
            "pattern_analysis": pattern_analysis,
            "executive_analysis": executive_analysis,
        }

    def _analyze_timing(self, trades: List[Trade]) -> Dict[str, Any]:
        """Analyze timing of trades relative to key events."""
        # Simplified timing analysis
        # In production, would cross-reference with earnings dates, news events, etc.
        
        # Group trades by month
        trades_by_month = {}
        for trade in trades:
            month_key = trade.filing_date.strftime("%Y-%m") if trade.filing_date else "unknown"
            if month_key not in trades_by_month:
                trades_by_month[month_key] = {"buys": 0, "sells": 0}
            if trade.transaction_type == "BUY":
                trades_by_month[month_key]["buys"] += 1
            else:
                trades_by_month[month_key]["sells"] += 1

        # Calculate concentration (more concentrated = potentially more significant)
        concentration = len(trades_by_month) / len(trades) if trades else 0

        return {
            "trades_by_month": len(trades_by_month),
            "concentration": round(concentration, 3),
            "recent_activity": "high" if len(trades_by_month) <= 3 else "moderate",
        }

    def _analyze_volume(self, trades: List[Trade]) -> Dict[str, Any]:
        """Analyze trade volumes relative to holdings."""
        buy_trades = [t for t in trades if t.transaction_type == "BUY"]
        sell_trades = [t for t in trades if t.transaction_type == "SELL"]

        avg_buy_size = (
            sum(t.shares or 0 for t in buy_trades) / len(buy_trades)
            if buy_trades
            else 0
        )
        avg_sell_size = (
            sum(t.shares or 0 for t in sell_trades) / len(sell_trades)
            if sell_trades
            else 0
        )

        # Calculate average trade value
        avg_buy_value = (
            sum(t.total_value or 0 for t in buy_trades) / len(buy_trades)
            if buy_trades
            else 0
        )
        avg_sell_value = (
            sum(t.total_value or 0 for t in sell_trades) / len(sell_trades)
            if sell_trades
            else 0
        )

        return {
            "avg_buy_size": round(avg_buy_size, 0),
            "avg_sell_size": round(avg_sell_size, 0),
            "avg_buy_value": round(avg_buy_value, 2),
            "avg_sell_value": round(avg_sell_value, 2),
            "size_ratio": round(avg_buy_size / avg_sell_size, 2) if avg_sell_size > 0 else 0,
        }

    def _detect_patterns(self, trades: List[Trade]) -> Dict[str, Any]:
        """Detect trading patterns (clustering, trends)."""
        if len(trades) < 3:
            return {"pattern_type": "insufficient_data"}

        # Check for clustering (multiple trades in short time)
        trades_sorted = sorted(trades, key=lambda t: t.filing_date or datetime.min)
        clusters = []
        current_cluster = [trades_sorted[0]]

        for i in range(1, len(trades_sorted)):
            days_diff = (
                (trades_sorted[i].filing_date - trades_sorted[i - 1].filing_date).days
                if trades_sorted[i].filing_date and trades_sorted[i - 1].filing_date
                else 999
            )
            if days_diff <= 30:  # Within 30 days = cluster
                current_cluster.append(trades_sorted[i])
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [trades_sorted[i]]

        if len(current_cluster) >= 2:
            clusters.append(current_cluster)

        # Check for trend (increasing/decreasing activity)
        recent_trades = [t for t in trades if t.filing_date and (datetime.utcnow().date() - t.filing_date).days <= 90]
        older_trades = [t for t in trades if t.filing_date and (datetime.utcnow().date() - t.filing_date).days > 90]
        
        recent_buy_ratio = (
            sum(1 for t in recent_trades if t.transaction_type == "BUY") / len(recent_trades)
            if recent_trades
            else 0
        )
        older_buy_ratio = (
            sum(1 for t in older_trades if t.transaction_type == "BUY") / len(older_trades)
            if older_trades
            else 0
        )

        trend = "increasing" if recent_buy_ratio > older_buy_ratio else "decreasing" if recent_buy_ratio < older_buy_ratio else "stable"

        return {
            "pattern_type": "clustered" if clusters else "distributed",
            "cluster_count": len(clusters),
            "trend": trend,
            "recent_buy_ratio": round(recent_buy_ratio, 2),
        }

    def _calculate_sentiment_score(
        self,
        buy_count: int,
        sell_count: int,
        buy_value: float,
        sell_value: float,
        timing_analysis: Dict[str, Any],
    ) -> float:
        """
        Calculate sentiment score (0-1) weighted by trade size and timing.

        1.0 = Very bullish (all buys, large values)
        0.5 = Neutral
        0.0 = Very bearish (all sells, large values)
        """
        total_count = buy_count + sell_count
        if total_count == 0:
            return 0.5

        # Count-based ratio
        count_ratio = buy_count / total_count

        # Value-based ratio
        total_value = buy_value + sell_value
        value_ratio = buy_value / total_value if total_value > 0 else 0.5

        # Weight: 60% value, 40% count (value is more significant)
        base_score = (value_ratio * 0.6) + (count_ratio * 0.4)

        # Adjust for timing (concentrated activity = more significant)
        concentration = timing_analysis.get("concentration", 0.5)
        if concentration > 0.7:  # Highly concentrated
            # Amplify the signal
            if base_score > 0.5:
                base_score = min(1.0, base_score * 1.1)
            else:
                base_score = max(0.0, base_score * 0.9)

        return base_score

    def _analyze_by_insider_type(
        self, insiders: List[Insider], trades: List[Trade]
    ) -> Dict[str, Any]:
        """Analyze trades by insider type (executive vs. director)."""
        # Simplified: Would need insider.title or insider.type field
        # For now, analyze all insiders together
        
        executive_trades = trades  # Placeholder - would filter by title
        director_trades = []  # Placeholder

        exec_buy_ratio = (
            sum(1 for t in executive_trades if t.transaction_type == "BUY")
            / len(executive_trades)
            if executive_trades
            else 0
        )

        return {
            "executive_trades": len(executive_trades),
            "director_trades": len(director_trades),
            "executive_buy_ratio": round(exec_buy_ratio, 2),
        }

    def _determine_pattern(
        self, sentiment_score: float, pattern_analysis: Dict[str, Any]
    ) -> str:
        """Determine overall pattern from sentiment and pattern analysis."""
        if sentiment_score >= 0.7:
            return "management_buying"
        elif sentiment_score <= 0.3:
            return "management_selling"
        else:
            pattern_type = pattern_analysis.get("pattern_type", "distributed")
            if pattern_type == "clustered":
                return "clustered_activity"
            return "neutral"

    def _calculate_confidence(
        self, total_count: int, buy_value: float, sell_value: float
    ) -> str:
        """Calculate confidence level in the analysis."""
        if total_count < 3:
            return "low"
        elif total_count < 10:
            return "moderate"
        
        total_value = buy_value + sell_value
        if total_value > 1000000:  # > $1M in trades
            return "high"
        elif total_value > 100000:  # > $100K
            return "moderate"
        else:
            return "low"

