"""
Scrape History Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScrapeHistoryBase(BaseModel):
    """Base schema for scrape history."""
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol")
    started_at: datetime = Field(..., description="When scrape started")


class ScrapeHistoryCreate(ScrapeHistoryBase):
    """Schema for creating scrape history record."""
    status: str = Field("running", max_length=20, description="Status: running, success, failed")


class ScrapeHistoryUpdate(BaseModel):
    """Schema for updating scrape history record."""
    completed_at: Optional[datetime] = Field(None, description="When scrape completed")
    status: Optional[str] = Field(None, max_length=20, description="Status: success or failed")
    filings_found: Optional[int] = Field(None, ge=0, description="Number of filings found")
    trades_created: Optional[int] = Field(None, ge=0, description="Number of trades created")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Duration in seconds")


class ScrapeHistoryRead(ScrapeHistoryBase):
    """Schema for reading scrape history."""
    id: int
    completed_at: Optional[datetime]
    status: str
    filings_found: int
    trades_created: int
    error_message: Optional[str]
    duration_seconds: Optional[float]
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class ScrapeStats(BaseModel):
    """Schema for scrape statistics."""
    total_scrapes: int = Field(..., description="Total number of scrapes executed")
    success_count: int = Field(..., description="Number of successful scrapes")
    failed_count: int = Field(..., description="Number of failed scrapes")
    avg_duration: float = Field(..., description="Average scrape duration in seconds")
    total_filings_found: int = Field(..., description="Total filings discovered")
    total_trades_created: int = Field(..., description="Total trades created")
