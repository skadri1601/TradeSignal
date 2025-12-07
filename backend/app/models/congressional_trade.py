"""
Congressional Trade model for TradeSignal.

Represents stock trading transactions by US Congressional members (House and Senate).
"""

from datetime import datetime, date
from typing import TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Date,
    DateTime,
    Boolean,
    Numeric,
    Text,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.congressperson import Congressperson


class TransactionType(str, Enum):
    """Enum for transaction types."""

    BUY = "BUY"
    SELL = "SELL"


class OwnerType(str, Enum):
    """Enum for ownership types in congressional disclosures."""

    SELF = "Self"
    SPOUSE = "Spouse"
    DEPENDENT_CHILD = "Dependent Child"
    JOINT = "Joint"


class CongressionalTrade(Base):
    """
    Congressional Trade model representing stock transactions by Congress members.

    Attributes:
        id: Primary key
        congressperson_id: Foreign key to Congressperson
        company_id: Foreign key to Company (nullable - some trades lack ticker)
        transaction_date: Date the transaction occurred
        disclosure_date: Date the trade was publicly disclosed
        transaction_type: BUY or SELL
        ticker: Stock ticker symbol (nullable if unresolved)
        asset_description: Full security name from filing
        amount_min: Lower bound of disclosed amount range
        amount_max: Upper bound of disclosed amount range
        amount_estimated: Midpoint estimate for analytics
        is_range_estimate: Whether amount is estimated from range
        owner_type: Who owns the asset (Self, Spouse, Dependent, Joint)
        asset_type: Type of asset (Stock, Bond, Option, etc.)
        disclosure_url: Link to official filing
        source: Data source (finnhub, senate_stock_watcher, manual)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "congressional_trades"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign Keys
    congressperson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("congresspeople.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Transaction Dates
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    disclosure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Transaction Details
    transaction_type: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )
    ticker: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    asset_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Amount Information (ranges from disclosures)
    amount_min: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    amount_max: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    amount_estimated: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True, index=True
    )
    is_range_estimate: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Congressional-Specific Fields
    owner_type: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Source Information
    disclosure_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="finnhub", nullable=False)

    # Additional Info
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    congressperson: Mapped["Congressperson"] = relationship(
        "Congressperson", back_populates="trades"
    )
    company: Mapped["Company"] = relationship(
        "Company", back_populates="congressional_trades"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('BUY', 'SELL')",
            name="check_congressional_transaction_type",
        ),
        # Composite index for efficient queries by congressperson and transaction date
        Index(
            "ix_congressperson_transaction_date",
            "congressperson_id",
            "transaction_date",
        ),
        # Composite index for company and transaction date
        Index(
            "ix_company_congressional_transaction_date",
            "company_id",
            "transaction_date",
        ),
        # Partial index for trades with resolved tickers
        Index(
            "ix_ticker_transaction_date",
            "ticker",
            "transaction_date",
            postgresql_where=(ticker.isnot(None)),
        ),
    )

    def __repr__(self) -> str:
        """String representation of CongressionalTrade."""
        return (
            f"<CongressionalTrade(id={self.id}, congressperson_id={self.congressperson_id}, "
            f"ticker={self.ticker}, type={self.transaction_type}, amount_estimated={self.amount_estimated})>"
        )

    @property
    def is_buy(self) -> bool:
        """Check if transaction is a buy."""
        return self.transaction_type == TransactionType.BUY.value

    @property
    def is_sell(self) -> bool:
        """Check if transaction is a sell."""
        return self.transaction_type == TransactionType.SELL.value

    @property
    def estimated_value(self) -> Decimal | None:
        """Get estimated value (prefers amount_estimated, falls back to midpoint calculation)."""
        if self.amount_estimated:
            return self.amount_estimated
        elif self.amount_min is not None and self.amount_max is not None:
            return (Decimal(self.amount_min) + Decimal(self.amount_max)) / 2
        return None

    @property
    def is_significant(self) -> bool:
        """Check if trade is significant (exceeds configured threshold)."""
        from app.config import settings

        estimated = self.estimated_value
        if estimated:
            return float(estimated) > settings.significant_trade_threshold
        return False

    @property
    def filing_delay_days(self) -> int | None:
        """Calculate delay between transaction and disclosure."""
        if self.transaction_date and self.disclosure_date:
            return (self.disclosure_date - self.transaction_date).days
        return None

    @property
    def amount_range_display(self) -> str:
        """Format amount range for display."""
        if self.amount_min and self.amount_max:
            return f"${self.amount_min:,.0f} - ${self.amount_max:,.0f}"
        elif self.amount_estimated:
            return f"~${self.amount_estimated:,.0f}"
        return "Unknown"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "congressperson_id": self.congressperson_id,
            "company_id": self.company_id,
            "transaction_date": self.transaction_date.isoformat()
            if self.transaction_date
            else None,
            "disclosure_date": self.disclosure_date.isoformat()
            if self.disclosure_date
            else None,
            "transaction_type": self.transaction_type,
            "ticker": self.ticker,
            "asset_description": self.asset_description,
            "amount_min": float(self.amount_min) if self.amount_min else None,
            "amount_max": float(self.amount_max) if self.amount_max else None,
            "amount_estimated": float(self.amount_estimated)
            if self.amount_estimated
            else None,
            "is_range_estimate": self.is_range_estimate,
            "owner_type": self.owner_type,
            "asset_type": self.asset_type,
            "disclosure_url": self.disclosure_url,
            "source": self.source,
            "comment": self.comment,
            "is_buy": self.is_buy,
            "is_sell": self.is_sell,
            "is_significant": self.is_significant,
            "filing_delay_days": self.filing_delay_days,
            "amount_range_display": self.amount_range_display,
            "estimated_value": float(self.estimated_value)
            if self.estimated_value
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
