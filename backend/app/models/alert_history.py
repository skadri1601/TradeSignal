"""
AlertHistory model for TradeSignal.

Logs every time an alert is triggered and a notification is sent.
Prevents duplicate notifications and provides audit trail.
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AlertHistory(Base):
    """
    Alert trigger history and notification delivery log.

    Records when alerts are triggered, which trades matched,
    which notification channels were used, and delivery status.
    """
    __tablename__ = "alert_history"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    alert_id = Column(
        Integer,
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the alert that was triggered"
    )
    trade_id = Column(
        Integer,
        ForeignKey("trades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the trade that triggered the alert"
    )

    # Notification Details
    notification_channel = Column(
        String(50),
        nullable=False,
        comment="Channel used: webhook, email, push"
    )
    notification_status = Column(
        String(50),
        nullable=False,
        comment="Delivery status: sent, failed, retrying"
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Error details if notification failed"
    )

    # Timestamp
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When the notification was sent"
    )

    # Relationships (optional, for ORM queries)
    # alert = relationship("Alert", back_populates="history")
    # trade = relationship("Trade", back_populates="alerts_triggered")

    def __repr__(self) -> str:
        return (
            f"<AlertHistory(id={self.id}, alert_id={self.alert_id}, "
            f"trade_id={self.trade_id}, channel='{self.notification_channel}', "
            f"status='{self.notification_status}')>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "trade_id": self.trade_id,
            "notification_channel": self.notification_channel,
            "notification_status": self.notification_status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
