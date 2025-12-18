"""
Webhook models for external integrations.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum

from app.database import Base


class WebhookEventType(str, Enum):
    """Types of webhook events."""
    TRADE_ALERT = "trade_alert"
    CONVERSION = "conversion"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    USER_SIGNED_UP = "user_signed_up"
    CUSTOM = "custom"


class WebhookStatus(str, Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookEndpoint(Base):
    """
    Webhook endpoint configuration.

    Attributes:
        id: Primary key
        user_id: Foreign key to User (owner)
        url: Webhook URL
        secret: Secret for signature verification
        event_types: JSON array of event types to subscribe to
        is_active: Whether webhook is active
        created_at: When webhook was created
        updated_at: When webhook was last updated
    """

    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str | None] = mapped_column(String(255), nullable=True)  # For HMAC signature
    event_types: Mapped[list | None] = mapped_column(JSON, nullable=True)  # List of event types
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class WebhookDelivery(Base):
    """
    Webhook delivery attempt record.

    Attributes:
        id: Primary key
        webhook_id: Foreign key to WebhookEndpoint
        event_type: Type of event
        payload: JSON payload sent
        status: Delivery status
        response_code: HTTP response code
        response_body: Response body
        attempts: Number of delivery attempts
        delivered_at: When webhook was successfully delivered
        created_at: When delivery was attempted
    """

    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    webhook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(WebhookStatus), nullable=False, default=WebhookStatus.PENDING, index=True
    )
    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    webhook: Mapped["WebhookEndpoint"] = relationship("WebhookEndpoint")

