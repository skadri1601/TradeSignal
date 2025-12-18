"""
Intrinsic Value Target (IVT) model for DCF-based stock valuation.

Stores DCF calculations and intrinsic value targets.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IntrinsicValueTarget(Base):
    """
    Store DCF-based intrinsic value targets for stocks.

    Attributes:
        id: Primary key
        ticker: Stock ticker symbol
        intrinsic_value: Calculated intrinsic value per share
        current_price: Stock price at calculation time
        discount_premium_pct: Discount/premium percentage
        wacc: Weighted Average Cost of Capital used
        terminal_growth_rate: Terminal growth rate assumption
        calculated_at: When IVT was calculated
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "intrinsic_value_targets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Valuation results
    intrinsic_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    current_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_premium_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False
    )  # Positive = discount, Negative = premium

    # Key assumptions
    wacc: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)  # e.g., 0.0850 = 8.50%
    terminal_growth_rate: Mapped[float] = mapped_column(
        Numeric(5, 4), nullable=False
    )  # e.g., 0.0250 = 2.50%

    # Revenue assumptions (stored as JSON in notes or separate fields)
    revenue_cagr: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    margin_assumptions: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    assumptions_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Full DCF assumptions as JSON

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_intrinsic_value_targets_ticker_calculated", "ticker", "calculated_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<IntrinsicValueTarget(ticker={self.ticker}, "
            f"ivt={self.intrinsic_value}, price={self.current_price})>"
        )

