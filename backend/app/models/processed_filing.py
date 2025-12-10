"""
ProcessedFiling model for TradeSignal.

Tracks SEC Form 4 filings that have already been processed to avoid
re-processing them on subsequent scrapes.
"""

from datetime import datetime, date, timezone
from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProcessedFiling(Base):
    """
    Model to track processed SEC Form 4 filings.

    Attributes:
        id: Primary key
        accession_number: SEC accession number (unique, indexed)
        filing_url: SEC filing URL (unique, indexed)
        filing_date: Date of filing
        ticker: Company ticker (indexed)
        trades_created: Number of trades created from this filing
        processed_at: When filing was processed
        created_at: Record creation timestamp
    """

    __tablename__ = "processed_filings"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Filing Identification
    accession_number: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    filing_url: Mapped[str] = mapped_column(
        String(500), nullable=False, unique=True, index=True
    )

    # Filing Metadata
    filing_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    ticker: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)

    # Processing Info
    trades_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("accession_number", name="uq_processed_filings_accession"),
        UniqueConstraint("filing_url", name="uq_processed_filings_url"),
        Index("ix_processed_filings_ticker_date", "ticker", "filing_date"),
    )

    def __repr__(self) -> str:
        """String representation of ProcessedFiling."""
        return (
            f"<ProcessedFiling(id={self.id}, accession_number={self.accession_number}, "
            f"ticker={self.ticker}, trades_created={self.trades_created})>"
        )

