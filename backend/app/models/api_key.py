"""
API Key Models for User API Authentication

Provides models for API key management and usage tracking.
"""

import secrets
import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserAPIKey(Base):
    """
    User API Key model for programmatic API access.

    API keys are hashed before storage and the plaintext key is only shown once on creation.
    """

    __tablename__ = "user_api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Security
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)  # SHA-256 hash
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)  # First 12 chars for display

    # Rate limiting
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    # Permissions
    can_read: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_write: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Lifecycle
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    usage_records: Mapped[list["APIKeyUsage"]] = relationship(
        "APIKeyUsage", back_populates="api_key", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_user_api_keys_user_active", "user_id", "is_active"),
    )

    @staticmethod
    def generate_key() -> tuple[str, str, str]:
        """
        Generate a new API key.

        Returns:
            tuple: (full_key, key_hash, key_prefix)
                - full_key: The complete API key (e.g., "ts_live_abc123...")
                - key_hash: SHA-256 hash of the key for storage
                - key_prefix: First 12 characters for display
        """
        # Generate secure random key
        random_part = secrets.token_urlsafe(32)  # 32 bytes = 43 chars base64
        full_key = f"ts_live_{random_part}"

        # Hash the key
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()

        # Get prefix for display
        key_prefix = full_key[:12]

        return (full_key, key_hash, key_prefix)

    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, name={self.name}, prefix={self.key_prefix})>"


class APIKeyUsage(Base):
    """
    API Key Usage tracking model.

    Records each API call made with an API key for analytics and rate limiting.
    """

    __tablename__ = "api_key_usage"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    api_key_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_api_keys.id", ondelete="CASCADE"), nullable=False, index=True
    )
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    api_key: Mapped["UserAPIKey"] = relationship("UserAPIKey", back_populates="usage_records")

    __table_args__ = (
        Index("idx_api_key_usage_key_timestamp", "api_key_id", "timestamp"),
    )

    def __repr__(self):
        return f"<APIKeyUsage(id={self.id}, api_key_id={self.api_key_id}, endpoint={self.endpoint}, timestamp={self.timestamp})>"

