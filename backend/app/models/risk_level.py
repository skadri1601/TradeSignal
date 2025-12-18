"""
Risk Level model for stock risk assessment.

Five-tier classification: Conservative, Moderate, Aggressive, Speculative, High Risk
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RiskLevel(str, Enum):
    """Risk level classification."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"
    HIGH = "high"


class RiskLevelAssessment(Base):
    """
    Store risk level assessments for stocks.

    Attributes:
        id: Primary key
        ticker: Stock ticker symbol
        risk_level: Risk classification (conservative, moderate, aggressive, speculative, high)
        score: Composite risk score (0-100, higher = more risky)
        earnings_volatility_score: Earnings volatility component (0-100)
        financial_leverage_score: Financial leverage component (0-100)
        operating_leverage_score: Operating leverage component (0-100)
        concentration_score: Business concentration component (0-100)
        industry_stability_score: Industry stability component (0-100)
        calculated_at: When assessment was calculated
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "risk_levels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Risk classification
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100 composite score

    # Component scores (0-100, higher = more risky)
    earnings_volatility_score: Mapped[float] = mapped_column(Float, nullable=False)
    financial_leverage_score: Mapped[float] = mapped_column(Float, nullable=False)
    operating_leverage_score: Mapped[float] = mapped_column(Float, nullable=False)
    concentration_score: Mapped[float] = mapped_column(Float, nullable=False)
    industry_stability_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI/ML insights

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_risk_levels_ticker_calculated", "ticker", "calculated_at"),
    )

    def __repr__(self) -> str:
        return f"<RiskLevelAssessment(ticker={self.ticker}, risk_level={self.risk_level}, score={self.score})>"

