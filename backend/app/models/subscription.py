"""
Subscription model for freemium/premium tier management.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User



class SubscriptionTier(str, Enum):
    """Subscription tier levels."""

    FREE = "free"
    BASIC = "basic"  # Kept for backward compatibility
    PLUS = "plus"  # New primary name for Plus tier
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
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )

    tier: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SubscriptionTier.FREE.value
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SubscriptionStatus.ACTIVE.value
    )

    # Stripe integration
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Admin tracking fields
    billing_period: Mapped[str | None] = mapped_column(String(10), nullable=True)
    price_paid: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    order_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True, index=True)
    stripe_order_number: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Billing period
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)

    # Trial
    trial_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Active flag (computed from status)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="subscription")

    def __repr__(self) -> str:
        return f"<Subscription(user_id={self.user_id}, tier={self.tier}, status={self.status})>"

    @property
    def is_premium(self) -> bool:
        """Check if user has any paid tier."""
        return self.tier in [
            SubscriptionTier.BASIC.value,
            SubscriptionTier.PLUS.value,
            SubscriptionTier.PRO.value,
            SubscriptionTier.ENTERPRISE.value,
        ]


# Tier limits configuration
# PORTFOLIO MODE: All features unlocked for free tier (for portfolio showcase)
TIER_LIMITS = {
    SubscriptionTier.FREE.value: {
        "ai_requests_limit": -1,  # Unlimited (portfolio mode)
        "alerts_max": -1,  # Unlimited (portfolio mode)
        "real_time_updates": True,  # Enabled (portfolio mode)
        "api_access": True,  # Enabled (portfolio mode)
        "research_api": True,  # Enabled (portfolio mode)
        "companies_tracked": -1,  # Unlimited (portfolio mode)
        "historical_data_days": -1,  # Unlimited (portfolio mode)
        "export_enabled": True,  # Enabled (portfolio mode)
        "advanced_screening": True,  # Enabled (portfolio mode)
    },
    SubscriptionTier.BASIC.value: { # Legacy/Starter
        "ai_requests_limit": 5,
        "alerts_max": 5,
        "real_time_updates": False,
        "api_access": False,
        "companies_tracked": 20,
        "historical_data_days": 90,
        "export_enabled": False,
        "advanced_screening": False,
    },
    SubscriptionTier.PLUS.value: { # Pro ($29/mo)
        "ai_requests_limit": 20,
        "alerts_max": 50,
        "real_time_updates": True,
        "api_access": False,
        "companies_tracked": 100,
        "historical_data_days": 730, # 2 Years
        "export_enabled": True,
        "advanced_screening": True,
    },
    SubscriptionTier.PRO.value: { # Premium / Research Pro ($49-99/mo)
        "ai_requests_limit": 100,
        "alerts_max": 200,
        "real_time_updates": True,
        "api_access": True, # Limited API access
        "research_api": True, # Research API access (IVT, Risk Levels, TS Score)
        "companies_tracked": -1, # Unlimited
        "historical_data_days": -1, # Unlimited
        "export_enabled": True,
        "advanced_screening": True,
    },
    SubscriptionTier.ENTERPRISE.value: {
        "ai_requests_limit": -1,
        "alerts_max": -1,
        "real_time_updates": True,
        "api_access": True,
        "research_api": True, # Full Research API access (all features)
        "companies_tracked": -1,
        "historical_data_days": -1,
        "export_enabled": True,
        "advanced_screening": True,
        "priority_support": True,
    },
}
