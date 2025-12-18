"""
Risk Level Assessment Service.

Calculates five-tier risk classification based on:
- Earnings volatility (40% weight)
- Financial leverage (25% weight)
- Operating leverage (20% weight)
- Business concentration (10% weight)
- Industry stability (5% weight)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.risk_level import RiskLevelAssessment, RiskLevel

logger = logging.getLogger(__name__)

# Component weights
WEIGHTS = {
    "earnings_volatility": 0.40,
    "financial_leverage": 0.25,
    "operating_leverage": 0.20,
    "concentration": 0.10,
    "industry_stability": 0.05,
}

# Risk level thresholds (composite score ranges)
RISK_THRESHOLDS = {
    RiskLevel.CONSERVATIVE: (0, 20),
    RiskLevel.MODERATE: (20, 40),
    RiskLevel.AGGRESSIVE: (40, 60),
    RiskLevel.SPECULATIVE: (60, 80),
    RiskLevel.HIGH: (80, 100),
}


class RiskLevelService:
    """Service for calculating and managing risk level assessments."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_risk_level(
        self,
        ticker: str,
        earnings_volatility: Optional[float] = None,
        debt_to_equity: Optional[float] = None,
        interest_coverage: Optional[float] = None,
        operating_leverage: Optional[float] = None,
        customer_concentration: Optional[float] = None,
        product_concentration: Optional[float] = None,
        industry_beta: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate risk level for a stock.

        Args:
            ticker: Stock ticker symbol
            earnings_volatility: Standard deviation of quarterly EPS growth (0-100)
            debt_to_equity: Debt-to-equity ratio
            interest_coverage: Interest coverage ratio
            operating_leverage: Operating leverage metric (0-100)
            customer_concentration: % revenue from top 10 customers
            product_concentration: % revenue from top 3 products
            industry_beta: Industry beta vs. market

        Returns:
            Dictionary with risk assessment
        """
        # Calculate component scores (0-100, higher = more risky)
        earnings_score = self._calculate_earnings_volatility_score(earnings_volatility)
        financial_score = self._calculate_financial_leverage_score(
            debt_to_equity, interest_coverage
        )
        operating_score = self._calculate_operating_leverage_score(operating_leverage)
        concentration_score = self._calculate_concentration_score(
            customer_concentration, product_concentration
        )
        industry_score = self._calculate_industry_stability_score(industry_beta)

        # Calculate weighted composite score
        composite_score = (
            earnings_score * WEIGHTS["earnings_volatility"]
            + financial_score * WEIGHTS["financial_leverage"]
            + operating_score * WEIGHTS["operating_leverage"]
            + concentration_score * WEIGHTS["concentration"]
            + industry_score * WEIGHTS["industry_stability"]
        )

        # Determine risk level
        risk_level = self._determine_risk_level(composite_score)

        return {
            "ticker": ticker,
            "risk_level": risk_level.value,
            "score": round(composite_score, 2),
            "component_scores": {
                "earnings_volatility": round(earnings_score, 2),
                "financial_leverage": round(financial_score, 2),
                "operating_leverage": round(operating_score, 2),
                "concentration": round(concentration_score, 2),
                "industry_stability": round(industry_score, 2),
            },
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def _calculate_earnings_volatility_score(self, volatility: Optional[float]) -> float:
        """Calculate earnings volatility score (0-100)."""
        if volatility is None:
            return 50.0  # Default moderate risk

        # Higher volatility = higher risk score
        # Normalize: assume 0-50% volatility maps to 0-100 score
        return min(100.0, max(0.0, volatility * 2))

    def _calculate_financial_leverage_score(
        self, debt_to_equity: Optional[float], interest_coverage: Optional[float]
    ) -> float:
        """Calculate financial leverage score (0-100)."""
        if debt_to_equity is None and interest_coverage is None:
            return 50.0  # Default moderate risk

        score = 0.0

        # Debt-to-equity component (0-60 points)
        if debt_to_equity is not None:
            if debt_to_equity < 0.5:
                score += 10  # Conservative
            elif debt_to_equity < 1.5:
                score += 30  # Moderate
            elif debt_to_equity < 3.0:
                score += 50  # Aggressive
            else:
                score += 60  # Speculative/High

        # Interest coverage component (0-40 points)
        if interest_coverage is not None:
            if interest_coverage > 10:
                score += 0  # Excellent coverage
            elif interest_coverage > 5:
                score += 15  # Good coverage
            elif interest_coverage > 2:
                score += 30  # Moderate coverage
            else:
                score += 40  # Poor coverage

        return min(100.0, score)

    def _calculate_operating_leverage_score(self, leverage: Optional[float]) -> float:
        """Calculate operating leverage score (0-100)."""
        if leverage is None:
            return 50.0  # Default moderate risk

        # Higher operating leverage = higher risk
        return min(100.0, max(0.0, leverage))

    def _calculate_concentration_score(
        self,
        customer_concentration: Optional[float],
        product_concentration: Optional[float],
    ) -> float:
        """Calculate business concentration score (0-100)."""
        if customer_concentration is None and product_concentration is None:
            return 50.0  # Default moderate risk

        scores = []
        if customer_concentration is not None:
            # Higher concentration = higher risk
            scores.append(min(100.0, customer_concentration))
        if product_concentration is not None:
            scores.append(min(100.0, product_concentration))

        return sum(scores) / len(scores) if scores else 50.0

    def _calculate_industry_stability_score(self, beta: Optional[float]) -> float:
        """Calculate industry stability score (0-100)."""
        if beta is None:
            return 50.0  # Default moderate risk

        # Higher beta = more volatility = higher risk
        # Beta typically ranges 0.5-2.0, map to 0-100
        if beta < 0.8:
            return 20.0  # Low volatility
        elif beta < 1.2:
            return 50.0  # Moderate volatility
        elif beta < 1.5:
            return 70.0  # High volatility
        else:
            return 90.0  # Very high volatility

    def _determine_risk_level(self, composite_score: float) -> RiskLevel:
        """Determine risk level from composite score."""
        for level, (min_score, max_score) in RISK_THRESHOLDS.items():
            if min_score <= composite_score < max_score:
                return level
        # Default to high risk if score >= 100
        return RiskLevel.HIGH

    async def get_latest_risk_level(self, ticker: str) -> Optional[RiskLevelAssessment]:
        """Get the latest risk level assessment for a ticker."""
        result = await self.db.execute(
            select(RiskLevelAssessment)
            .where(RiskLevelAssessment.ticker == ticker.upper())
            .order_by(RiskLevelAssessment.calculated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_risk_assessment(
        self, assessment_data: Dict[str, Any], notes: Optional[str] = None
    ) -> RiskLevelAssessment:
        """Save risk assessment to database."""
        assessment = RiskLevelAssessment(
            ticker=assessment_data["ticker"].upper(),
            risk_level=assessment_data["risk_level"],
            score=assessment_data["score"],
            earnings_volatility_score=assessment_data["component_scores"][
                "earnings_volatility"
            ],
            financial_leverage_score=assessment_data["component_scores"][
                "financial_leverage"
            ],
            operating_leverage_score=assessment_data["component_scores"][
                "operating_leverage"
            ],
            concentration_score=assessment_data["component_scores"]["concentration"],
            industry_stability_score=assessment_data["component_scores"][
                "industry_stability"
            ],
            calculated_at=datetime.fromisoformat(assessment_data["calculated_at"]),
            notes=notes,
        )

        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        return assessment

