"""
TradeSignal Score model for storing calculated scores.

Stores TS Score calculations for stocks with timestamps
for historical tracking and caching.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TradeSignalScore(Base):
    """
    Store TradeSignal Score calculations.

    Attributes:
        id: Primary key
        ticker: Stock ticker symbol
        score: TS Score (1-5)
        p_ivt_ratio: Price to IVT ratio
        current_price: Stock price at calculation time
        intrinsic_value_target: IVT at calculation time
        risk_level: Risk level used for calculation
        calculated_at: When score was calculated
        created_at: When record was created
    """

    __tablename__ = "tradesignal_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Score data
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    p_ivt_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    intrinsic_value_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    discount_premium_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Risk and metadata
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rating: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "Strong Buy"

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_tradesignal_scores_ticker_calculated", "ticker", "calculated_at"),
    )

    def __repr__(self) -> str:
        return f"<TradeSignalScore(ticker={self.ticker}, score={self.score}, calculated_at={self.calculated_at})>"

