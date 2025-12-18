"""
Competitive Strength Rating model.

Five-tier system: Dominant, Advantaged, Competitive, Vulnerable, Weak
Based on five sources: Network Effects, Intangible Assets, Cost Advantages,
Switching Costs, Efficient Scale
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CompetitiveStrength(str, Enum):
    """Competitive strength rating."""

    DOMINANT = "dominant"
    ADVANTAGED = "advantaged"
    COMPETITIVE = "competitive"
    VULNERABLE = "vulnerable"
    WEAK = "weak"


class CompetitiveStrengthRating(Base):
    """
    Store competitive strength ratings for stocks.

    Attributes:
        id: Primary key
        ticker: Stock ticker symbol
        rating: Competitive strength rating
        composite_score: Composite score (0-10 points)
        network_effects_score: Network effects score (0-2 points)
        intangible_assets_score: Intangible assets score (0-2 points)
        cost_advantages_score: Cost advantages score (0-2 points)
        switching_costs_score: Switching costs score (0-2 points)
        efficient_scale_score: Efficient scale score (0-2 points)
        trajectory: Competitive trajectory (strengthening/stable/weakening)
        calculated_at: When rating was calculated
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "competitive_strength_ratings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Rating and composite score
    rating: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-10 points

    # Component scores (0-2 points each)
    network_effects_score: Mapped[float] = mapped_column(Float, nullable=False)
    intangible_assets_score: Mapped[float] = mapped_column(Float, nullable=False)
    cost_advantages_score: Mapped[float] = mapped_column(Float, nullable=False)
    switching_costs_score: Mapped[float] = mapped_column(Float, nullable=False)
    efficient_scale_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Trajectory indicator
    trajectory: Mapped[str] = mapped_column(
        String(20), nullable=False, default="stable"
    )  # strengthening, stable, weakening

    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_competitive_strength_ticker_calculated", "ticker", "calculated_at"),
    )

    def __repr__(self) -> str:
        return f"<CompetitiveStrengthRating(ticker={self.ticker}, rating={self.rating}, score={self.composite_score})>"

