"""
Competitive Strength Rating Service.

Five-tier system: Dominant, Advantaged, Competitive, Vulnerable, Weak
Based on five sources analysis:
- Network Effects (0-2 points)
- Intangible Assets (0-2 points)
- Cost Advantages (0-2 points)
- Switching Costs (0-2 points)
- Efficient Scale (0-2 points)

Total: 0-10 points composite score
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.competitive_strength import CompetitiveStrengthRating, CompetitiveStrength
from app.services.financial_data_service import FinancialDataService

logger = logging.getLogger(__name__)

# Rating thresholds (composite score ranges)
RATING_THRESHOLDS = {
    CompetitiveStrength.DOMINANT: (8.5, 10.0),
    CompetitiveStrength.ADVANTAGED: (7.0, 8.5),
    CompetitiveStrength.COMPETITIVE: (5.0, 7.0),
    CompetitiveStrength.VULNERABLE: (3.0, 5.0),
    CompetitiveStrength.WEAK: (0.0, 3.0),
}


class CompetitiveStrengthService:
    """Service for calculating competitive strength ratings."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.financial_data_service = FinancialDataService()

    async def calculate_competitive_strength(
        self,
        ticker: str,
        network_effects: Optional[float] = None,  # 0-2 points
        intangible_assets: Optional[float] = None,  # 0-2 points
        cost_advantages: Optional[float] = None,  # 0-2 points
        switching_costs: Optional[float] = None,  # 0-2 points
        efficient_scale: Optional[float] = None,  # 0-2 points
    ) -> Dict[str, Any]:
        """
        Calculate competitive strength rating.

        Args:
            ticker: Stock ticker symbol
            network_effects: Network effects score (0-2) - if None, will fetch from financial data
            intangible_assets: Intangible assets score (0-2) - if None, will fetch from financial data
            cost_advantages: Cost advantages score (0-2) - if None, will fetch from financial data
            switching_costs: Switching costs score (0-2) - if None, will fetch from financial data
            efficient_scale: Efficient scale score (0-2) - if None, will fetch from financial data

        Returns:
            Dictionary with competitive strength assessment
        """
        # Fetch real financial data if components not provided
        if any(score is None for score in [network_effects, intangible_assets, cost_advantages, switching_costs, efficient_scale]):
            logger.info(f"Fetching financial data for competitive strength calculation: {ticker}")
            components = await self.financial_data_service.calculate_competitive_strength_components(ticker)
            network_effects = network_effects if network_effects is not None else components["network_effects"]
            intangible_assets = intangible_assets if intangible_assets is not None else components["intangible_assets"]
            cost_advantages = cost_advantages if cost_advantages is not None else components["cost_advantages"]
            switching_costs = switching_costs if switching_costs is not None else components["switching_costs"]
            efficient_scale = efficient_scale if efficient_scale is not None else components["efficient_scale"]
        
        # Validate all components are available (no hardcoded defaults)
        if network_effects is None:
            raise ValueError(f"Network effects score not available for {ticker}")
        if intangible_assets is None:
            raise ValueError(f"Intangible assets score not available for {ticker}")
        if cost_advantages is None:
            raise ValueError(f"Cost advantages score not available for {ticker}")
        if switching_costs is None:
            raise ValueError(f"Switching costs score not available for {ticker}")
        if efficient_scale is None:
            raise ValueError(f"Efficient scale score not available for {ticker}")
        
        # Clamp scores to 0-2 range
        network_effects = max(0.0, min(2.0, network_effects))
        intangible_assets = max(0.0, min(2.0, intangible_assets))
        cost_advantages = max(0.0, min(2.0, cost_advantages))
        switching_costs = max(0.0, min(2.0, switching_costs))
        efficient_scale = max(0.0, min(2.0, efficient_scale))

        # Calculate composite score (sum of all components)
        composite_score = (
            network_effects
            + intangible_assets
            + cost_advantages
            + switching_costs
            + efficient_scale
        )

        # Determine rating
        rating = self._determine_rating(composite_score)

        # Determine trajectory (simplified - would need historical comparison)
        trajectory = self._determine_trajectory(composite_score)

        return {
            "ticker": ticker,
            "rating": rating.value,
            "composite_score": round(composite_score, 2),
            "component_scores": {
                "network_effects": round(network_effects, 2),
                "intangible_assets": round(intangible_assets, 2),
                "cost_advantages": round(cost_advantages, 2),
                "switching_costs": round(switching_costs, 2),
                "efficient_scale": round(efficient_scale, 2),
            },
            "trajectory": trajectory,
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def _determine_rating(self, composite_score: float) -> CompetitiveStrength:
        """Determine rating from composite score."""
        for rating, (min_score, max_score) in RATING_THRESHOLDS.items():
            if min_score <= composite_score < max_score:
                return rating
        # Default to weak if score < 0
        return CompetitiveStrength.WEAK

    def _determine_trajectory(self, composite_score: float) -> str:
        """
        Determine competitive trajectory.

        Simplified version - would need historical comparison for accuracy.
        """
        if composite_score >= 8.0:
            return "strengthening"
        elif composite_score >= 5.0:
            return "stable"
        else:
            return "weakening"

    async def get_latest_rating(
        self, ticker: str
    ) -> Optional[CompetitiveStrengthRating]:
        """Get the latest competitive strength rating for a ticker."""
        result = await self.db.execute(
            select(CompetitiveStrengthRating)
            .where(CompetitiveStrengthRating.ticker == ticker.upper())
            .order_by(CompetitiveStrengthRating.calculated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

