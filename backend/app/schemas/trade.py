"""
Pydantic schemas for Trade model.

Handles request/response validation and serialization.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.models.trade import TransactionType

from app.schemas.company import CompanyRead
from app.schemas.insider import InsiderRead


class TradeBase(BaseModel):
    """Base schema with shared fields."""
    insider_id: Optional[int] = Field(None, description="Insider ID")
    company_id: Optional[int] = Field(None, description="Company ID")
    transaction_date: date = Field(..., description="Transaction date")
    filing_date: date = Field(..., description="Filing date")
    transaction_type: str = Field(..., description="BUY or SELL")
    transaction_code: Optional[str] = Field(None, max_length=2, description="SEC transaction code")
    shares: Decimal = Field(..., gt=0, description="Number of shares")
    price_per_share: Optional[Decimal] = Field(None, ge=0, description="Price per share in USD")
    total_value: Optional[Decimal] = Field(None, ge=0, description="Total transaction value")
    shares_owned_after: Optional[Decimal] = Field(None, ge=0, description="Shares owned after transaction")
    ownership_type: Optional[str] = Field(None, max_length=20, description="Direct or Indirect")
    derivative_transaction: bool = Field(False, description="Is derivative/options trade")
    sec_filing_url: Optional[str] = Field(None, description="URL to SEC filing")
    form_type: str = Field("Form 4", max_length=10, description="Form type")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        """Validate transaction type is BUY or SELL."""
        v = v.upper().strip()
        if v not in [TransactionType.BUY.value, TransactionType.SELL.value]:
            raise ValueError("transaction_type must be 'BUY' or 'SELL'")
        return v

    @field_validator("transaction_code")
    @classmethod
    def validate_transaction_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate and uppercase transaction code."""
        if v:
            return v.upper().strip()
        return v


class TradeCreate(TradeBase):
    """Schema for creating a new trade."""
    pass


class TradeUpdate(BaseModel):
    """Schema for updating a trade (all fields optional)."""
    insider_id: Optional[int] = None
    company_id: Optional[int] = None
    transaction_date: Optional[date] = None
    filing_date: Optional[date] = None
    transaction_type: Optional[str] = None
    transaction_code: Optional[str] = Field(None, max_length=2)
    shares: Optional[Decimal] = Field(None, gt=0)
    price_per_share: Optional[Decimal] = Field(None, ge=0)
    total_value: Optional[Decimal] = Field(None, ge=0)
    shares_owned_after: Optional[Decimal] = Field(None, ge=0)
    ownership_type: Optional[str] = Field(None, max_length=20)
    derivative_transaction: Optional[bool] = None
    sec_filing_url: Optional[str] = None
    form_type: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate transaction type."""
        if v:
            v = v.upper().strip()
            if v not in [TransactionType.BUY.value, TransactionType.SELL.value]:
                raise ValueError("transaction_type must be 'BUY' or 'SELL'")
        return v


class TradeRead(TradeBase):
    """Schema for reading trade data (includes id and timestamps)."""
    id: int = Field(..., description="Trade ID")
    is_buy: bool = Field(..., description="Is this a buy transaction")
    is_sell: bool = Field(..., description="Is this a sell transaction")
    is_significant: bool = Field(..., description="Is trade significant (>$100k)")
    filing_delay_days: Optional[int] = Field(None, description="Days between transaction and filing")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class TradeWithDetails(TradeRead):
    """Trade schema with nested company and insider data.

    Use PEP 604 union types (X | None) to avoid runtime evaluation issues
    with Optional[...] under Pydantic's forward-ref handling.
    """
    company: "CompanyRead | None" = Field(None, description="Company details")
    insider: "InsiderRead | None" = Field(None, description="Insider details")
    current_stock_price: float | None = Field(None, description="Current stock price")
    price_change_percent: float | None = Field(None, description="Price change since trade")
    profit_loss: float | None = Field(None, description="Profit/loss amount")


class TradeFilter(BaseModel):
    """Schema for trade filtering parameters."""
    company_id: Optional[int] = Field(None, description="Filter by company")
    insider_id: Optional[int] = Field(None, description="Filter by insider")
    ticker: Optional[str] = Field(None, description="Filter by ticker symbol")
    transaction_type: Optional[str] = Field(None, description="Filter by BUY or SELL")
    transaction_date_from: Optional[date] = Field(None, description="Start date")
    transaction_date_to: Optional[date] = Field(None, description="End date")
    min_value: Optional[float] = Field(None, ge=0, description="Minimum trade value")
    max_value: Optional[float] = Field(None, ge=0, description="Maximum trade value")
    min_shares: Optional[float] = Field(None, ge=0, description="Minimum shares")
    derivative_only: Optional[bool] = Field(None, description="Show only derivative trades")
    significant_only: Optional[bool] = Field(None, description="Show only significant trades (>$100k)")


class TradeStats(BaseModel):
    """Schema for trade statistics."""
    total_trades: int = Field(0, description="Total number of trades")
    total_buys: int = Field(0, description="Total buy transactions")
    total_sells: int = Field(0, description="Total sell transactions")
    total_shares_traded: float = Field(0.0, description="Total shares traded")
    total_value: float = Field(0.0, description="Total dollar value")
    average_trade_size: float = Field(0.0, description="Average trade size")
    largest_trade: Optional[float] = Field(None, description="Largest single trade")
    most_active_company: Optional[str] = Field(None, description="Most traded company ticker")
    most_active_insider: Optional[str] = Field(None, description="Most active insider name")
