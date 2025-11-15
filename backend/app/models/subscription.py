"""
Subscription model for freemium/premium tier management.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class Subscription(Base):
    """
    User subscription and tier management.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        tier: Subscription tier (free/basic/pro/enterprise)
        status: Subscription status
        stripe_customer_id: Stripe customer ID
        stripe_subscription_id: Stripe subscription ID
        current_period_start: Billing period start
        current_period_end: Billing period end
        cancel_at_period_end: Whether subscription cancels at end
        created_at: When subscription was created
        updated_at: When subscription was last updated
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    tier: Mapped[str] = mapped_column(String(20), nullable=False, default=SubscriptionTier.FREE.value)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=SubscriptionStatus.ACTIVE.value)

    # Stripe integration
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Billing period
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)

    # Trial
    trial_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Active flag (computed from status)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Subscription(user_id={self.user_id}, tier={self.tier}, status={self.status})>"

    @property
    def is_premium(self) -> bool:
        """Check if user has any paid tier."""
        return self.tier in [SubscriptionTier.BASIC.value, SubscriptionTier.PRO.value, SubscriptionTier.ENTERPRISE.value]


# Tier limits configuration
TIER_LIMITS = {
    SubscriptionTier.FREE.value: {
        "ai_requests_per_day": 5,
        "alerts_max": 3,
        "real_time_updates": False,
        "api_access": False,
        "companies_tracked": 10,
        "historical_data_days": 30,
    },
    SubscriptionTier.BASIC.value: {
        "ai_requests_per_day": 50,
        "alerts_max": 20,
        "real_time_updates": True,
        "api_access": False,
        "companies_tracked": 50,
        "historical_data_days": 365,
    },
    SubscriptionTier.PRO.value: {
        "ai_requests_per_day": 500,
        "alerts_max": 100,
        "real_time_updates": True,
        "api_access": True,
        "companies_tracked": -1,  # Unlimited
        "historical_data_days": -1,  # Unlimited
    },
    SubscriptionTier.ENTERPRISE.value: {
        "ai_requests_per_day": -1,  # Unlimited
        "alerts_max": -1,  # Unlimited
        "real_time_updates": True,
        "api_access": True,
        "companies_tracked": -1,  # Unlimited
        "historical_data_days": -1,  # Unlimited
        "priority_support": True,
        "custom_integrations": True,
    },
}
