"""
Pydantic schemas for API Key API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(..., min_length=3, max_length=100, description="API key name/identifier")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    rate_limit_per_hour: int = Field(1000, ge=1, le=10000, description="Requests per hour limit")
    permissions: Dict[str, bool] = Field(
        default={"read": True, "write": False, "delete": False},
        description="Permission flags"
    )
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Days until expiration")


class APIKeyResponse(BaseModel):
    """Schema for API key response (without plaintext key)."""

    id: int
    name: str
    description: Optional[str]
    key_prefix: str
    rate_limit_per_hour: int
    can_read: bool
    can_write: bool
    can_delete: bool
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(BaseModel):
    """Schema for API key creation response (includes plaintext key - shown only once)."""

    api_key: APIKeyResponse
    key: str = Field(..., description="Plaintext API key - shown only once, save it securely!")


class APIKeyUsageStats(BaseModel):
    """Schema for API key usage statistics."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    days: int

