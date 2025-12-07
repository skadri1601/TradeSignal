"""
Payment/Order History Model for TradeSignal.

Tracks all payment transactions and subscription orders.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class PaymentStatus(str, Enum):
    """Payment status."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class PaymentType(str, Enum):
    """Payment type."""

    SUBSCRIPTION = "subscription"
    UPGRADE = "upgrade"
    RENEWAL = "renewal"
    ONE_TIME = "one_time"


class Payment(Base):
    """
    Payment/Order history model.

    Tracks all payment transactions including:
    - Subscription purchases
    - Upgrades/downgrades
    - Renewals
    - Refunds
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Payment Details
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    payment_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # subscription, upgrade, renewal, one_time
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PaymentStatus.PENDING.value
    )

    # Tier Information
    tier: Mapped[str] = mapped_column(String(20), nullable=False)
    tier_before: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # For upgrades/downgrades

    # Stripe Integration
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    stripe_charge_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # Billing Period
    period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    invoice_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Refund Information
    refunded_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refund_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"
