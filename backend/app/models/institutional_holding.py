"""
Institutional Holdings model for 13F filings.

Tracks quarterly position changes from hedge funds and institutional investors.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InstitutionalHolding(Base):
    """
    Store institutional holdings from 13F filings.

    Attributes:
        id: Primary key
        institution_name: Name of the institution
        cik: Central Index Key of the institution
        ticker: Stock ticker symbol
        company_id: Foreign key to Company
        shares: Number of shares held
        value: Total value of holding
        filing_date: Date of 13F filing
        period_end: Period end date for the filing
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "institutional_holdings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    cik: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Stock information
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Holding details
    shares: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Filing information
    filing_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_institutional_holdings_ticker_period", "ticker", "period_end"),
        Index("ix_institutional_holdings_cik_period", "cik", "period_end"),
    )

    def __repr__(self) -> str:
        return (
            f"<InstitutionalHolding(institution={self.institution_name}, "
            f"ticker={self.ticker}, shares={self.shares})>"
        )


class InstitutionalPositionChange(Base):
    """
    Track quarterly position changes for institutional holdings.

    Calculates changes between periods to identify smart money flow.
    """

    __tablename__ = "institutional_position_changes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    institution_cik: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Period information
    previous_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Position changes
    previous_shares: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    current_shares: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    shares_change: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    shares_change_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Value changes
    previous_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    current_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    value_change: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Action classification
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # NEW, INCREASED, DECREASED, SOLD_OUT

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_position_changes_ticker_period", "ticker", "current_period_end"),
        Index("ix_position_changes_cik_period", "institution_cik", "current_period_end"),
    )

    def __repr__(self) -> str:
        return (
            f"<InstitutionalPositionChange(cik={self.institution_cik}, "
            f"ticker={self.ticker}, action={self.action})>"
        )

