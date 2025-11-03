"""
Pydantic schemas for push notification subscriptions.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PushSubscriptionCreate(BaseModel):
    """Schema for creating a new push subscription."""

    endpoint: str = Field(..., description="Push service endpoint URL")
    p256dh_key: str = Field(..., description="Client public key for encryption (base64)")
    auth_key: str = Field(..., description="Authentication secret (base64)")
    user_agent: str | None = Field(None, description="Browser/device info")


class PushSubscriptionResponse(BaseModel):
    """Schema for push subscription responses."""

    id: int
    endpoint: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_notified_at: datetime | None = None

    model_config = {"from_attributes": True}


class PushSubscriptionDelete(BaseModel):
    """Schema for deleting a push subscription."""

    endpoint: str = Field(..., description="Endpoint to unsubscribe")
