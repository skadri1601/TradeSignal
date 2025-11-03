"""
Push subscription model for browser push notifications.
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class PushSubscription(Base):
    """
    Browser push notification subscription.

    Stores Web Push API subscription info for each user/device.
    """

    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, unique=True, nullable=False, index=True)
    p256dh_key = Column(String, nullable=False)  # Encryption key
    auth_key = Column(String, nullable=False)  # Authentication secret
    user_agent = Column(String, nullable=True)  # Browser/device info
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_notified_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<PushSubscription(id={self.id}, endpoint={self.endpoint[:50]}...)>"
