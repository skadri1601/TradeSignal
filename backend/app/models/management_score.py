"""
Management Excellence Score model.

A/B/C/D/F grading system based on:
- M&A track record (30%)
- Capital discipline (25%)
- Shareholder returns (20%)
- Leverage management (15%)
- Governance (10%)
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ManagementGrade(str, Enum):
    """Management excellence grade."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class ManagementScore(Base):
    """
    Store management excellence scores for stocks.

    Attributes:
        id: Primary key
        ticker: Stock ticker symbol
        grade: Management grade (A/B/C/D/F)
        composite_score: Composite score (0-100)
        m_and_a_score: M&A track record score (30% weight)
        capital_discipline_score: Capital discipline score (25% weight)
        shareholder_returns_score: Shareholder returns score (20% weight)
        leverage_management_score: Leverage management score (15% weight)
        governance_score: Governance score (10% weight)
        calculated_at: When score was calculated
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "management_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Grade and composite score
    grade: Mapped[str] = mapped_column(String(1), nullable=False, index=True)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100

    # Component scores (0-100)
    m_and_a_score: Mapped[float] = mapped_column(Float, nullable=False)
    capital_discipline_score: Mapped[float] = mapped_column(Float, nullable=False)
    shareholder_returns_score: Mapped[float] = mapped_column(Float, nullable=False)
    leverage_management_score: Mapped[float] = mapped_column(Float, nullable=False)
    governance_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI/NLP insights

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_management_scores_ticker_calculated", "ticker", "calculated_at"),
    )

    def __repr__(self) -> str:
        return f"<ManagementScore(ticker={self.ticker}, grade={self.grade}, score={self.composite_score})>"

