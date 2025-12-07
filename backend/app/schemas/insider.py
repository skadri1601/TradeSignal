"""
Pydantic schemas for Insider model.

Handles request/response validation and serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.company import CompanyRead


class InsiderBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Insider's full name"
    )
    title: Optional[str] = Field(None, max_length=255, description="Job title")
    relationship: Optional[str] = Field(
        None, max_length=100, description="Relationship to company"
    )
    company_id: Optional[int] = Field(None, description="Company ID")
    is_director: bool = Field(False, description="Is board director")
    is_officer: bool = Field(False, description="Is corporate officer")
    is_ten_percent_owner: bool = Field(False, description="Owns 10%+ of company stock")
    is_other: bool = Field(False, description="Other relationship")


class InsiderCreate(InsiderBase):
    """Schema for creating a new insider."""

    pass


class InsiderUpdate(BaseModel):
    """Schema for updating an insider (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    relationship: Optional[str] = Field(None, max_length=100)
    company_id: Optional[int] = None
    is_director: Optional[bool] = None
    is_officer: Optional[bool] = None
    is_ten_percent_owner: Optional[bool] = None
    is_other: Optional[bool] = None


class InsiderRead(InsiderBase):
    """Schema for reading insider data (includes id and timestamps)."""

    id: int = Field(..., description="Insider ID")
    primary_role: str = Field(..., description="Primary role")
    roles: List[str] = Field(default_factory=list, description="All roles")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle computed properties."""
        if hasattr(obj, "to_dict"):
            return super().model_validate(obj.to_dict())
        return super().model_validate(obj)


class InsiderWithCompany(InsiderRead):
    """Insider schema with nested company data."""

    company: Optional[CompanyRead] = Field(None, description="Associated company")


class InsiderWithStats(InsiderRead):
    """Insider schema with trading statistics."""

    total_trades: int = Field(0, description="Total number of trades")
    total_shares_bought: float = Field(0.0, description="Total shares bought")
    total_shares_sold: float = Field(0.0, description="Total shares sold")
    total_buy_value: float = Field(0.0, description="Total value of purchases")
    total_sell_value: float = Field(0.0, description="Total value of sales")
    win_rate: Optional[float] = Field(
        None, description="Percentage of profitable trades"
    )
