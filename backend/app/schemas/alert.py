"""
Pydantic schemas for Alert API endpoints.

Request/response validation for alert management.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    """Base schema with common alert fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Alert name")
    alert_type: str = Field(
        ...,
        description="Alert type: large_trade, company_watch, insider_role, volume_spike",
    )
    ticker: Optional[str] = Field(None, max_length=10, description="Filter by ticker")
    min_value: Optional[float] = Field(
        None, ge=0, description="Minimum trade value USD"
    )
    max_value: Optional[float] = Field(
        None, ge=0, description="Maximum trade value USD"
    )
    transaction_type: Optional[str] = Field(None, description="BUY or SELL")
    insider_roles: list[str] = Field(
        default_factory=list, description="Insider role filters"
    )
    notification_channels: list[str] = Field(
        ..., min_length=1, description="webhook, email, push"
    )
    webhook_url: Optional[str] = Field(
        None, description="Webhook URL for notifications"
    )
    email: Optional[str] = Field(
        None, max_length=255, description="Email for notifications"
    )
    is_active: bool = Field(default=True, description="Whether alert is enabled")

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v: str) -> str:
        """Validate alert type is one of allowed values."""
        allowed = ["large_trade", "company_watch", "insider_role", "volume_spike"]
        if v not in allowed:
            raise ValueError(f"alert_type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate transaction type if provided."""
        if v is not None and v not in ["BUY", "SELL"]:
            raise ValueError("transaction_type must be BUY or SELL")
        return v

    @field_validator("notification_channels")
    @classmethod
    def validate_notification_channels(cls, v: list[str]) -> list[str]:
        """Validate notification channels."""
        allowed = ["webhook", "email", "push"]
        for channel in v:
            if channel not in allowed:
                raise ValueError(
                    f"Invalid channel '{channel}'. Must be one of: {', '.join(allowed)}"
                )
        return v

    @field_validator("min_value", "max_value")
    @classmethod
    def validate_value_range(cls, v: Optional[float]) -> Optional[float]:
        """Ensure values are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Trade values must be non-negative")
        return v

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook URL format if provided."""
        if v is not None:
            if not v.startswith("https://"):
                raise ValueError("Webhook URL must start with https://")
        return v


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""

    pass


class AlertUpdate(BaseModel):
    """Schema for updating an existing alert (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    alert_type: Optional[str] = None
    ticker: Optional[str] = Field(None, max_length=10)
    min_value: Optional[float] = Field(None, ge=0)
    max_value: Optional[float] = Field(None, ge=0)
    transaction_type: Optional[str] = None
    insider_roles: Optional[list[str]] = None
    notification_channels: Optional[list[str]] = Field(None, min_length=1)
    webhook_url: Optional[str] = None
    email: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate alert type if provided."""
        if v is not None:
            allowed = ["large_trade", "company_watch", "insider_role", "volume_spike"]
            if v not in allowed:
                raise ValueError(f"alert_type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate transaction type if provided."""
        if v is not None and v not in ["BUY", "SELL", None]:
            raise ValueError("transaction_type must be BUY or SELL")
        return v


class AlertResponse(AlertBase):
    """Schema for alert API responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertToggle(BaseModel):
    """Schema for toggling alert active status."""

    is_active: bool


class AlertTestNotification(BaseModel):
    """Schema for sending test notifications."""

    pass  # No fields needed, just triggers a test


class AlertHistoryResponse(BaseModel):
    """Schema for alert history responses."""

    id: int
    alert_id: int
    trade_id: int
    notification_channel: str
    notification_status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertStatsResponse(BaseModel):
    """Schema for alert statistics."""

    total_alerts: int
    active_alerts: int
    inactive_alerts: int
    total_notifications_sent: int
    notifications_last_24h: int
    failed_notifications_last_24h: int
