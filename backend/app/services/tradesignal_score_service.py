"""
TradeSignal Score (TS Score) Service

Calculates a 1-5 rating based on price vs. Intrinsic Value Target (IVT)
and risk-adjusted thresholds.

TS Score Interpretation:
- 5 = Significantly Undervalued (Strong Buy)
- 4 = Moderately Undervalued (Buy)
- 3 = Fairly Valued (Hold)
- 2 = Moderately Overvalued (Caution)
- 1 = Significantly Overvalued (Sell)
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Risk-adjusted thresholds for TS Score calculation
# Format: {risk_level: {score: (min_p_ivt, max_p_ivt)}}
TS_SCORE_THRESHOLDS = {
    "conservative": {
        5: (0.0, 0.85),
        4: (0.85, 0.95),
        3: (0.95, 1.05),
        2: (1.05, 1.15),
        1: (1.15, float("inf")),
    },
    "moderate": {
        5: (0.0, 0.75),
        4: (0.75, 0.90),
        3: (0.90, 1.10),
        2: (1.10, 1.25),
        1: (1.25, float("inf")),
    },
    "aggressive": {
        5: (0.0, 0.65),
        4: (0.65, 0.85),
        3: (0.85, 1.15),
        2: (1.15, 1.35),
        1: (1.35, float("inf")),
    },
    "speculative": {
        5: (0.0, 0.55),
        4: (0.55, 0.80),
        3: (0.80, 1.20),
        2: (1.20, 1.45),
        1: (1.45, float("inf")),
    },
    "high": {
        5: (0.0, 0.50),
        4: (0.50, 0.75),
        3: (0.75, 1.25),
        2: (1.25, 1.50),
        1: (1.50, float("inf")),
    },
}


class TradeSignalScoreService:
    """Service for calculating and managing TradeSignal Scores."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def calculate_ts_score(
        self,
        current_price: float,
        intrinsic_value_target: Optional[float],
        risk_level: str = "moderate",
    ) -> Dict[str, Any]:
        """
        Calculate TS Score based on price, IVT, and risk level.

        Args:
            current_price: Current stock price
            intrinsic_value_target: Intrinsic Value Target (IVT)
            risk_level: Risk level (conservative, moderate, aggressive, speculative, high)

        Returns:
            Dictionary with score, ratio, and metadata
        """
        if not intrinsic_value_target or intrinsic_value_target <= 0:
            return {
                "score": None,
                "p_ivt_ratio": None,
                "risk_level": risk_level,
                "message": "IVT not available",
                "calculated_at": datetime.utcnow().isoformat(),
            }

        # Calculate P/IVT ratio
        p_ivt_ratio = current_price / intrinsic_value_target

        # Get thresholds for risk level
        risk_level_lower = risk_level.lower()
        if risk_level_lower not in TS_SCORE_THRESHOLDS:
            logger.warning(f"Unknown risk level: {risk_level}, defaulting to moderate")
            risk_level_lower = "moderate"

        thresholds = TS_SCORE_THRESHOLDS[risk_level_lower]

        # Find matching score
        score = 3  # Default to "Fairly Valued"
        for score_value, (min_ratio, max_ratio) in thresholds.items():
            if min_ratio <= p_ivt_ratio < max_ratio:
                score = score_value
                break

        # Determine rating label
        rating_labels = {
            5: "Significantly Undervalued",
            4: "Moderately Undervalued",
            3: "Fairly Valued",
            2: "Moderately Overvalued",
            1: "Significantly Overvalued",
        }

        # Calculate discount/premium percentage
        discount_premium = ((intrinsic_value_target - current_price) / intrinsic_value_target) * 100

        return {
            "score": score,
            "p_ivt_ratio": round(p_ivt_ratio, 4),
            "current_price": current_price,
            "intrinsic_value_target": intrinsic_value_target,
            "discount_premium_pct": round(discount_premium, 2),
            "risk_level": risk_level_lower,
            "rating": rating_labels[score],
            "calculated_at": datetime.utcnow().isoformat(),
        }

    async def get_ts_score_for_ticker(
        self,
        ticker: str,
        current_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get TS Score for a ticker symbol.

        This is a placeholder that will be enhanced once IVT and risk level
        data infrastructure is in place.

        Args:
            ticker: Stock ticker symbol
            current_price: Optional current price (will fetch if not provided)

        Returns:
            TS Score data
        """
        # TODO: Fetch IVT from database once IVT infrastructure is built
        # TODO: Fetch risk level from database once risk level infrastructure is built
        # TODO: Fetch current price from market data service if not provided

        # Placeholder implementation
        logger.warning(
            f"TS Score calculation for {ticker} - IVT and risk level infrastructure not yet implemented"
        )

        return {
            "ticker": ticker,
            "score": None,
            "message": "IVT and risk level data required for TS Score calculation",
            "status": "pending_implementation",
        }

    def get_score_color(self, score: Optional[int]) -> str:
        """Get color class for score badge."""
        if score is None:
            return "gray"
        if score >= 4:
            return "green"  # Buy/Strong Buy
        if score == 3:
            return "yellow"  # Hold
        return "red"  # Sell/Caution

    def get_score_badge_label(self, score: Optional[int]) -> str:
        """Get badge label for score."""
        if score is None:
            return "N/A"
        labels = {
            5: "Strong Buy",
            4: "Buy",
            3: "Hold",
            2: "Caution",
            1: "Sell",
        }
        return labels.get(score, "N/A")

