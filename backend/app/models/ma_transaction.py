"""
M&A Transaction model for tracking merger and acquisition history.

Tracks M&A deals to calculate management M&A track record scores.
"""

from datetime import datetime, date
from sqlalchemy import String, Float, Date, DateTime, Text, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MATransaction(Base):
    """
    Model to track M&A transactions for companies.

    Attributes:
        id: Primary key
        company_id: Foreign key to Company
        ticker: Company ticker (denormalized for easier querying)
        deal_type: Type of deal (acquisition, merger, divestiture, etc.)
        target_company: Name of target company
        deal_value: Deal value in USD
        deal_date: Date of deal announcement/completion
        status: Deal status (announced, completed, terminated)
        roi: Return on investment (if calculable)
        integration_success: Success rating (0-100) if available
        notes: Additional notes about the deal
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "ma_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Deal Information
    deal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # acquisition, merger, divestiture
    target_company: Mapped[str] = mapped_column(String(200), nullable=False)
    deal_value: Mapped[float | None] = mapped_column(Float, nullable=True)  # USD
    deal_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="announced")  # announced, completed, terminated

    # Performance Metrics
    roi: Mapped[float | None] = mapped_column(Float, nullable=True)  # Return on investment percentage
    integration_success: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100 rating

    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Data source (FMP, SEC, manual)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_ma_transactions_ticker_date", "ticker", "deal_date"),
        Index("ix_ma_transactions_company_date", "company_id", "deal_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<MATransaction(id={self.id}, ticker={self.ticker}, "
            f"target={self.target_company}, value={self.deal_value})>"
        )

