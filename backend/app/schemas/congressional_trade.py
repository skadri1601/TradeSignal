"""
Pydantic schemas for CongressionalTrade model.

Handles request/response validation and serialization for congressional stock trades.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.models.congressional_trade import TransactionType, OwnerType

from app.schemas.company import CompanyRead
from app.schemas.congressperson import CongresspersonRead


class CongressionalTradeBase(BaseModel):
    """Base schema with shared fields."""

    congressperson_id: int = Field(..., description="Congressperson ID")
    company_id: Optional[int] = Field(
        None, description="Company ID (nullable if ticker unresolved)"
    )
    transaction_date: date = Field(..., description="Transaction date")
    disclosure_date: date = Field(..., description="Date trade was publicly disclosed")
    transaction_type: str = Field(..., description="BUY or SELL")
    ticker: Optional[str] = Field(
        None, max_length=10, description="Stock ticker symbol"
    )
    asset_description: str = Field(..., description="Full security name from filing")
    amount_min: Optional[Decimal] = Field(
        None, ge=0, description="Lower bound of amount range"
    )
    amount_max: Optional[Decimal] = Field(
        None, ge=0, description="Upper bound of amount range"
    )
    amount_estimated: Optional[Decimal] = Field(
        None, ge=0, description="Estimated midpoint value"
    )
    is_range_estimate: bool = Field(
        True, description="Whether amount is estimated from range"
    )
    owner_type: str = Field(
        ..., description="Who owns the asset (Self, Spouse, Dependent Child, Joint)"
    )
    asset_type: Optional[str] = Field(
        None, max_length=50, description="Type of asset (Stock, Bond, Option, etc.)"
    )
    disclosure_url: Optional[str] = Field(None, description="URL to official filing")
    source: str = Field("finnhub", max_length=50, description="Data source")
    comment: Optional[str] = Field(None, description="Additional notes")

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        """Validate transaction type is BUY or SELL."""
        v = v.upper().strip()
        if v not in [TransactionType.BUY.value, TransactionType.SELL.value]:
            raise ValueError("transaction_type must be 'BUY' or 'SELL'")
        return v

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: Optional[str]) -> Optional[str]:
        """Validate and uppercase ticker."""
        if v:
            return v.upper().strip()
        return v

    @field_validator("owner_type")
    @classmethod
    def validate_owner_type(cls, v: str) -> str:
        """Validate owner type."""
        valid_types = [
            OwnerType.SELF.value,
            OwnerType.SPOUSE.value,
            OwnerType.DEPENDENT_CHILD.value,
            OwnerType.JOINT.value,
        ]
        if v not in valid_types:
            raise ValueError(f"owner_type must be one of: {', '.join(valid_types)}")
        return v


class CongressionalTradeCreate(CongressionalTradeBase):
    """Schema for creating a new congressional trade."""

    pass


class CongressionalTradeUpdate(BaseModel):
    """Schema for updating a congressional trade (all fields optional)."""

    congressperson_id: Optional[int] = None
    company_id: Optional[int] = None
    transaction_date: Optional[date] = None
    disclosure_date: Optional[date] = None
    transaction_type: Optional[str] = None
    ticker: Optional[str] = Field(None, max_length=10)
    asset_description: Optional[str] = None
    amount_min: Optional[Decimal] = Field(None, ge=0)
    amount_max: Optional[Decimal] = Field(None, ge=0)
    amount_estimated: Optional[Decimal] = Field(None, ge=0)
    is_range_estimate: Optional[bool] = None
    owner_type: Optional[str] = None
    asset_type: Optional[str] = Field(None, max_length=50)
    disclosure_url: Optional[str] = None
    source: Optional[str] = Field(None, max_length=50)
    comment: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate transaction type."""
        if v:
            v = v.upper().strip()
            if v not in [TransactionType.BUY.value, TransactionType.SELL.value]:
                raise ValueError("transaction_type must be 'BUY' or 'SELL'")
        return v

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: Optional[str]) -> Optional[str]:
        """Validate and uppercase ticker."""
        if v:
            return v.upper().strip()
        return v


class CongressionalTradeRead(CongressionalTradeBase):
    """Schema for reading congressional trade data (includes id and timestamps)."""

    id: int = Field(..., description="Trade ID")
    is_buy: bool = Field(..., description="Is this a buy transaction")
    is_sell: bool = Field(..., description="Is this a sell transaction")
    is_significant: bool = Field(..., description="Is trade significant (>$100k)")
    filing_delay_days: Optional[int] = Field(
        None, description="Days between transaction and disclosure"
    )
    estimated_value: Optional[Decimal] = Field(
        None, description="Best estimate of trade value"
    )
    amount_range_display: str = Field(
        ..., description="Formatted amount range for display"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CongressionalTradeWithDetails(CongressionalTradeRead):
    """Congressional trade schema with nested congressperson and company data.

    Use PEP 604 union types (X | None) to avoid runtime evaluation issues.
    """

    congressperson: "CongresspersonRead | None" = Field(
        None, description="Congressperson details"
    )
    company: "CompanyRead | None" = Field(None, description="Company details")
    current_stock_price: float | None = Field(None, description="Current stock price")
    price_change_percent: float | None = Field(
        None, description="Price change since trade"
    )


class CongressionalTradeFilter(BaseModel):
    """Schema for congressional trade filtering parameters."""

    congressperson_id: Optional[int] = Field(
        None, description="Filter by congressperson"
    )
    company_id: Optional[int] = Field(None, description="Filter by company")
    ticker: Optional[str] = Field(None, description="Filter by ticker symbol")
    chamber: Optional[str] = Field(None, description="Filter by HOUSE or SENATE")
    state: Optional[str] = Field(
        None, max_length=2, description="Filter by state (2-letter code)"
    )
    party: Optional[str] = Field(None, description="Filter by party")
    transaction_type: Optional[str] = Field(None, description="Filter by BUY or SELL")
    owner_type: Optional[str] = Field(None, description="Filter by owner type")
    transaction_date_from: Optional[date] = Field(None, description="Start date")
    transaction_date_to: Optional[date] = Field(None, description="End date")
    min_value: Optional[float] = Field(None, ge=0, description="Minimum trade value")
    max_value: Optional[float] = Field(None, ge=0, description="Maximum trade value")
    significant_only: Optional[bool] = Field(
        None, description="Show only significant trades (>$100k)"
    )

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        """Validate and uppercase state code."""
        if v:
            return v.upper().strip()
        return v


class CongressionalTradeStats(BaseModel):
    """Schema for congressional trade statistics."""

    total_trades: int = Field(0, description="Total number of trades")
    total_buys: int = Field(0, description="Total buy transactions")
    total_sells: int = Field(0, description="Total sell transactions")
    total_value: float = Field(0.0, description="Net volume (BUY value - SELL value)")
    total_buy_value: float = Field(0.0, description="Total dollar value of buys")
    total_sell_value: float = Field(0.0, description="Total dollar value of sells")
    average_trade_size: float = Field(0.0, description="Average trade size")
    largest_trade: Optional[float] = Field(None, description="Largest single trade")
    most_active_congressperson: Optional[str] = Field(
        None, description="Most active member name"
    )
    most_active_company: Optional[str] = Field(
        None, description="Most traded company ticker"
    )
    house_trade_count: int = Field(0, description="Number of House trades")
    senate_trade_count: int = Field(0, description="Number of Senate trades")
    democrat_buy_count: int = Field(0, description="Democrat buy count")
    democrat_sell_count: int = Field(0, description="Democrat sell count")
    republican_buy_count: int = Field(0, description="Republican buy count")
    republican_sell_count: int = Field(0, description="Republican sell count")
