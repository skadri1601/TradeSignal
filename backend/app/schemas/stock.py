"""
Pydantic schemas for Stock/Ticker validation.

Provides input validation and sanitization for stock ticker symbols.
"""

import re
import html
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TickerRequest(BaseModel):
    """Schema for validating stock ticker symbols."""

    ticker: str = Field(
        ..., min_length=1, max_length=10, description="Stock ticker symbol"
    )

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """
        Validate ticker format.

        Only allows uppercase alphanumeric characters (1-10 chars).
        Prevents SQL injection, XSS, and other malicious inputs.
        """
        v = v.upper().strip()
        if not re.match(r"^[A-Z0-9]{1,10}$", v):
            raise ValueError(
                "Invalid ticker format. Must be 1-10 uppercase alphanumeric characters."
            )
        return v


class WatchlistCreate(BaseModel):
    """Schema for creating a watchlist."""

    name: str = Field(..., min_length=1, max_length=100, description="Watchlist name")
    tickers: List[str] = Field(
        ..., min_items=1, max_items=50, description="List of ticker symbols"
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """
        Sanitize watchlist name to prevent XSS attacks.

        Escapes HTML entities and removes leading/trailing whitespace.
        """
        sanitized = html.escape(v.strip())
        if len(sanitized) < 1:
            raise ValueError("Name cannot be empty")
        if len(sanitized) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        return sanitized

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        """
        Validate all tickers in the list.

        Ensures each ticker is properly formatted and safe.
        """
        validated = []
        for ticker in v:
            ticker = ticker.upper().strip()
            if not re.match(r"^[A-Z0-9]{1,10}$", ticker):
                raise ValueError(
                    f"Invalid ticker: {ticker}. Must be 1-10 uppercase alphanumeric characters."
                )
            validated.append(ticker)

        # Remove duplicates while preserving order
        seen = set()
        unique_validated = []
        for ticker in validated:
            if ticker not in seen:
                seen.add(ticker)
                unique_validated.append(ticker)

        return unique_validated


class UserCreate(BaseModel):
    """Schema for user registration (if auth is implemented)."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Requires:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password cannot exceed 128 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class StockQuoteValidator(BaseModel):
    """
    Comprehensive validator for stock quote data.

    Based on TRUTH_FREE.md Phase 3.3 - Data Validation.
    Ensures quote data is valid, reasonable, and safe to use.
    """

    symbol: str = Field(
        ..., min_length=1, max_length=10, description="Stock ticker symbol"
    )
    current_price: float = Field(..., gt=0, description="Current stock price")
    previous_close: float = Field(..., gt=0, description="Previous close price")
    open_price: Optional[float] = Field(None, gt=0, description="Opening price")
    day_high: Optional[float] = Field(None, gt=0, description="Day high price")
    day_low: Optional[float] = Field(None, gt=0, description="Day low price")
    volume: Optional[int] = Field(None, ge=0, description="Trading volume")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Ensure symbol is non-empty and uppercase."""
        if not v or len(v) < 1:
            raise ValueError("Symbol cannot be empty")
        return v.upper()

    @field_validator("current_price")
    @classmethod
    def validate_price_range(cls, v: float) -> float:
        """
        Validate price is reasonable.

        Sanity check: price should be between $0.01 and $1,000,000
        """
        if v < 0.01:
            raise ValueError(f"Price {v} too low (minimum $0.01)")
        if v > 1000000:
            raise ValueError(f"Price {v} seems unrealistic (maximum $1,000,000)")
        return v

    @field_validator("day_high")
    @classmethod
    def validate_high_vs_low(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure day_high >= day_low if both are provided."""
        if v is not None and "day_low" in info.data:
            day_low = info.data.get("day_low")
            if day_low is not None and v < day_low:
                logger.warning(f"day_high ({v}) < day_low ({day_low}), correcting")
                # Fix: Swap them
                return day_low
        return v

    @field_validator("current_price")
    @classmethod
    def validate_price_within_day_range(cls, v: float, info) -> float:
        """
        Check if current price is within day range (with 5% buffer).

        Logs warning if price is outside expected range but allows it
        (price might be from after-hours trading).
        """
        day_low = info.data.get("day_low")
        day_high = info.data.get("day_high")

        if day_low is not None and day_high is not None:
            # Allow 5% buffer for price fluctuations
            min_price = day_low * 0.95
            max_price = day_high * 1.05

            if not (min_price <= v <= max_price):
                logger.warning(
                    f"Price {v} outside day range [{day_low}, {day_high}] "
                    f"(with 5% buffer: [{min_price:.2f}, {max_price:.2f}])"
                )

        return v

    model_config = {"str_strip_whitespace": True, "validate_assignment": True}
