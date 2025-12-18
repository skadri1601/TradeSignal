"""
Feature usage log model for tracking feature access attempts.

Tracks individual feature access attempts for analytics, billing,
and understanding feature adoption.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeatureUsageLog(Base):
    """
    Track individual feature access attempts.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        feature_key: Key identifying the feature (e.g., 'api_access', 'export_enabled')
        feature_name: Human-readable feature name
        tier_required: Minimum tier required for this feature
        user_tier: User's tier at time of access attempt
        access_granted: Whether access was granted or denied
        request_path: API endpoint path
        request_method: HTTP method
        ip_address: User's IP address
        user_agent: User's browser/client user agent
        created_at: When the access attempt was made
    """

    __tablename__ = "feature_usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Feature identification
    feature_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    feature_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tier information
    tier_required: Mapped[str | None] = mapped_column(String(20), nullable=True)
    user_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Access result
    access_granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    # Request metadata
    request_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_feature_usage_logs_user_feature", "user_id", "feature_key"),
        Index("ix_feature_usage_logs_analytics", "created_at", "feature_key", "access_granted"),
    )

    def __repr__(self) -> str:
        return (
            f"<FeatureUsageLog(id={self.id}, user_id={self.user_id}, "
            f"feature={self.feature_key}, granted={self.access_granted})>"
        )

