"""
Trade model for TradeSignal.

Represents individual insider trading transactions from SEC Form 4.
"""

from datetime import datetime, date
from typing import TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, Boolean, Numeric, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.insider import Insider


class TransactionType(str, Enum):
    """Enum for transaction types."""
    BUY = "BUY"
    SELL = "SELL"


class TransactionCode(str, Enum):
    """
    SEC Form 4 transaction codes.

    Common codes:
    - P: Purchase (open market or private)
    - S: Sale (open market or private)
    - A: Grant/Award
    - M: Exercise of options
    - G: Gift
    - F: Payment of exercise price or tax liability
    - D: Disposition (other than sale)
    """
    P = "P"  # Purchase
    S = "S"  # Sale
    A = "A"  # Grant/Award
    M = "M"  # Exercise of options
    G = "G"  # Gift
    F = "F"  # Payment of tax
    D = "D"  # Disposition
    C = "C"  # Conversion
    J = "J"  # Other acquisition
    K = "K"  # Other disposition


class Trade(Base):
    """
    Trade model representing insider trading transactions.

    Attributes:
        id: Primary key
        insider_id: Foreign key to Insider
        company_id: Foreign key to Company
        transaction_date: Date the transaction occurred
        filing_date: Date the Form 4 was filed with SEC
        transaction_type: BUY or SELL
        transaction_code: SEC transaction code (P, S, A, M, etc.)
        shares: Number of shares traded
        price_per_share: Price per share in USD
        total_value: Total transaction value (shares * price)
        shares_owned_after: Shares owned after transaction
        ownership_type: Direct or Indirect ownership
        derivative_transaction: True if options/derivatives trade
        sec_filing_url: URL to SEC filing
        form_type: Form type (usually "Form 4")
        notes: Additional notes
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "trades"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign Keys
    insider_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("insiders.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    company_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Transaction Dates
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    filing_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Transaction Details
    transaction_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )
    transaction_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # Share Information
    shares: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    price_per_share: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True, index=True)
    shares_owned_after: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)

    # Ownership Details
    ownership_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    derivative_transaction: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # SEC Filing Info
    sec_filing_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    form_type: Mapped[str] = mapped_column(String(10), default="Form 4", nullable=False)

    # Additional Info
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    insider: Mapped["Insider"] = relationship("Insider", back_populates="trades")
    company: Mapped["Company"] = relationship("Company", back_populates="trades")

    # Constraints
    __table_args__ = (
        CheckConstraint("transaction_type IN ('BUY', 'SELL')", name="check_transaction_type"),
    )

    def __repr__(self) -> str:
        """String representation of Trade."""
        return (
            f"<Trade(id={self.id}, company_id={self.company_id}, "
            f"type={self.transaction_type}, shares={self.shares})>"
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
    def calculated_total_value(self) -> Decimal | None:
        """Calculate total value from shares and price."""
        if self.shares and self.price_per_share:
            return Decimal(self.shares) * Decimal(self.price_per_share)
        return self.total_value

    @property
    def is_significant(self) -> bool:
        """Check if trade is significant (>$100k)."""
        if self.total_value:
            return float(self.total_value) > 100000
        elif self.calculated_total_value:
            return float(self.calculated_total_value) > 100000
        return False

    @property
    def filing_delay_days(self) -> int | None:
        """Calculate delay between transaction and filing."""
        if self.transaction_date and self.filing_date:
            return (self.filing_date - self.transaction_date).days
        return None

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "insider_id": self.insider_id,
            "company_id": self.company_id,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "filing_date": self.filing_date.isoformat() if self.filing_date else None,
            "transaction_type": self.transaction_type,
            "transaction_code": self.transaction_code,
            "shares": float(self.shares) if self.shares else None,
            "price_per_share": float(self.price_per_share) if self.price_per_share else None,
            "total_value": float(self.total_value) if self.total_value else None,
            "shares_owned_after": float(self.shares_owned_after) if self.shares_owned_after else None,
            "ownership_type": self.ownership_type,
            "derivative_transaction": self.derivative_transaction,
            "sec_filing_url": self.sec_filing_url,
            "form_type": self.form_type,
            "notes": self.notes,
            "is_buy": self.is_buy,
            "is_sell": self.is_sell,
            "is_significant": self.is_significant,
            "filing_delay_days": self.filing_delay_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
