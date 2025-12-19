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
from app.services.financial_data_service import FinancialDataService
from app.services.ma_tracking_service import MATrackingService
from app.services.insider_pattern_analyzer import InsiderPatternAnalyzer

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
        self.financial_data_service = FinancialDataService()
        self.ma_tracking_service = MATrackingService(db)
        self.insider_analyzer = InsiderPatternAnalyzer(db)

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
        # Fetch real financial data if components not provided
        if any(score is None for score in [m_and_a_track_record, capital_discipline, shareholder_returns, leverage_management, governance]):
            logger.info(f"Fetching financial data for management score calculation: {ticker}")
            
            # Fetch M&A track record score
            if m_and_a_track_record is None:
                # Sync M&A transactions first
                await self.ma_tracking_service.sync_ma_transactions(ticker)
                m_and_a_track_record = await self.ma_tracking_service.calculate_ma_track_record_score(ticker)
                # If no M&A history, calculate estimate from financial data
                if m_and_a_track_record is None:
                    financials = await self.financial_data_service.fetch_company_financials(ticker)
                    if financials:
                        # Use company financial health as proxy for M&A track record
                        roe = financials.get("roe", 0) * 100
                        revenue = financials.get("revenue", 0)
                        if revenue > 0 and roe > 0:
                            # Estimate: healthier companies (higher ROE) tend to have better M&A track records
                            m_and_a_track_record = min(100.0, max(30.0, roe * 0.8))
                        else:
                            raise ValueError(f"Cannot estimate M&A track record for {ticker}: insufficient financial data")
                    else:
                        raise ValueError(f"Cannot calculate M&A track record for {ticker}: financial data unavailable")
            
            # Fetch other components from financial data (pass db for M&A tracking)
            financial_components = await self.financial_data_service.calculate_management_score_components(ticker, db=self.db)
            capital_discipline = capital_discipline if capital_discipline is not None else financial_components["capital_discipline"]
            shareholder_returns = shareholder_returns if shareholder_returns is not None else financial_components["shareholder_returns"]
            leverage_management = leverage_management if leverage_management is not None else financial_components["leverage_management"]
            governance = governance if governance is not None else financial_components["governance"]
            m_and_a_track_record = m_and_a_track_record if m_and_a_track_record is not None else financial_components["m_and_a"]
        
        # Validate all components are available (no hardcoded defaults)
        if m_and_a_track_record is None:
            raise ValueError(f"M&A track record score not available for {ticker}")
        if capital_discipline is None:
            raise ValueError(f"Capital discipline score not available for {ticker}")
        if shareholder_returns is None:
            raise ValueError(f"Shareholder returns score not available for {ticker}")
        if leverage_management is None:
            raise ValueError(f"Leverage management score not available for {ticker}")
        if governance is None:
            raise ValueError(f"Governance score not available for {ticker}")
        
        m_and_a = m_and_a_track_record
        capital = capital_discipline
        returns = shareholder_returns
        leverage = leverage_management
        gov = governance

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
        # Use enhanced insider pattern analyzer
        insider_insights_data = await self.insider_analyzer.analyze_insider_patterns(ticker)
        
        # Convert to format expected by existing code
        insider_insights = {
            "insider_activity": insider_insights_data.get("insider_activity", "No recent activity"),
            "pattern": insider_insights_data.get("pattern", "neutral"),
            "insight": self._generate_insight_from_pattern(insider_insights_data),
            "buy_ratio": insider_insights_data.get("sentiment_score", 0.5),
            "confidence": insider_insights_data.get("confidence", "low"),
        }

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

    def _generate_insight_from_pattern(self, pattern_data: Dict[str, Any]) -> str:
        """Generate human-readable insight from pattern analysis."""
        pattern = pattern_data.get("pattern", "neutral")
        sentiment_score = pattern_data.get("sentiment_score", 0.5)
        confidence = pattern_data.get("confidence", "low")
        
        if pattern == "management_buying" and sentiment_score >= 0.7:
            return f"Management showing strong conviction through buying activity (confidence: {confidence})"
        elif pattern == "management_selling" and sentiment_score <= 0.3:
            return f"Management selling activity may indicate concerns (confidence: {confidence})"
        elif pattern == "clustered_activity":
            return "Clustered insider trading activity suggests significant events or decisions"
        else:
            return "Mixed insider trading activity with neutral sentiment"

    async def get_latest_score(self, ticker: str) -> Optional[ManagementScore]:
        """Get the latest management score for a ticker."""
        result = await self.db.execute(
            select(ManagementScore)
            .where(ManagementScore.ticker == ticker.upper())
            .order_by(ManagementScore.calculated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

