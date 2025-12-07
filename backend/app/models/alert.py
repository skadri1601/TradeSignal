"""
Alert model for TradeSignal.

Stores user-defined alert rules that trigger notifications when
matching insider trades are detected.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DECIMAL,
    Text,
    TIMESTAMP,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from app.database import Base


class Alert(Base):
    """
    Alert rule configuration.

    Defines conditions for triggering notifications when insider trades occur.
    Supports multiple notification channels (webhook, email, push).
    """

    __tablename__ = "alerts"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Alert Configuration
    name = Column(String(255), nullable=False, comment="User-friendly alert name")
    alert_type = Column(
        String(50),
        nullable=False,
        comment="Alert type: large_trade, company_watch, insider_role, volume_spike",
    )

    # Filter Criteria
    ticker = Column(
        String(10),
        nullable=True,
        index=True,
        comment="Filter by specific ticker (e.g., NVDA, TSLA)",
    )
    min_value = Column(
        DECIMAL(20, 2), nullable=True, comment="Minimum trade value in USD"
    )
    max_value = Column(
        DECIMAL(20, 2), nullable=True, comment="Maximum trade value in USD"
    )
    transaction_type = Column(
        String(10), nullable=True, comment="Filter by BUY or SELL"
    )
    insider_roles = Column(
        JSON,
        nullable=True,
        comment="Filter by insider roles (CEO, CFO, Director, etc.) - stored as JSON array",
    )

    # Notification Configuration
    notification_channels = Column(
        JSON,
        nullable=False,
        comment="Channels to send notifications: webhook, email, push - stored as JSON array",
    )
    webhook_url = Column(
        Text,
        nullable=True,
        comment="Slack/Discord webhook URL or custom HTTPS endpoint",
    )
    email = Column(
        String(255), nullable=True, comment="Email address to send notifications"
    )

    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether alert is enabled",
    )

    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When alert was created",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="When alert was last updated",
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, name='{self.name}', type='{self.alert_type}', active={self.is_active})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "alert_type": self.alert_type,
            "ticker": self.ticker,
            "min_value": float(self.min_value) if self.min_value else None,
            "max_value": float(self.max_value) if self.max_value else None,
            "transaction_type": self.transaction_type,
            "insider_roles": self.insider_roles or [],
            "notification_channels": self.notification_channels or [],
            "webhook_url": self.webhook_url,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
