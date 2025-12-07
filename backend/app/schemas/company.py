"""
Pydantic schemas for Company model.

Handles request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CompanyBase(BaseModel):
    """Base schema with shared fields."""

    ticker: str = Field(
        ..., min_length=1, max_length=10, description="Stock ticker symbol"
    )
    name: Optional[str] = Field(None, max_length=255, description="Company name")
    cik: str = Field(
        ..., min_length=10, max_length=10, description="SEC Central Index Key"
    )
    sector: Optional[str] = Field(None, max_length=100, description="Business sector")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    market_cap: Optional[int] = Field(
        None, ge=0, description="Market capitalization in USD"
    )
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(
        None, max_length=255, description="Company website URL"
    )

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_uppercase(cls, v: str) -> str:
        """Ensure ticker is uppercase."""
        return v.upper().strip()

    @field_validator("cik")
    @classmethod
    def cik_must_be_valid(cls, v: str) -> str:
        """Ensure CIK is valid format (10 digits)."""
        v = v.strip()
        if not v.isdigit():
            raise ValueError("CIK must contain only digits")
        if len(v) != 10:
            raise ValueError("CIK must be exactly 10 digits")
        return v


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""

    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company (all fields optional)."""

    ticker: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, max_length=255)
    cik: Optional[str] = Field(None, min_length=10, max_length=10)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_uppercase(cls, v: Optional[str]) -> Optional[str]:
        """Ensure ticker is uppercase."""
        return v.upper().strip() if v else None


class CompanyRead(CompanyBase):
    """Schema for reading company data (includes id and timestamps)."""

    id: int = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True  # Allow creation from SQLAlchemy models


class CompanyWithStats(CompanyRead):
    """Company schema with additional statistics."""

    total_trades: int = Field(0, description="Total number of trades")
    total_insiders: int = Field(0, description="Total number of insiders")
    recent_buy_count: int = Field(0, description="Recent buy transactions")
    recent_sell_count: int = Field(0, description="Recent sell transactions")


class CompanySearch(BaseModel):
    """Schema for company search parameters."""

    query: Optional[str] = Field(
        None, min_length=1, description="Search query (ticker or name)"
    )
    sector: Optional[str] = Field(None, description="Filter by sector")
    min_market_cap: Optional[int] = Field(None, ge=0, description="Minimum market cap")
    max_market_cap: Optional[int] = Field(None, ge=0, description="Maximum market cap")
