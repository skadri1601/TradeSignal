"""
Scrape Job Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScrapeJobBase(BaseModel):
    """Base schema for scrape job."""
    job_id: str = Field(..., max_length=100, description="APScheduler job ID")
    job_type: str = Field(..., max_length=50, description="Job type")
    ticker: Optional[str] = Field(None, max_length=10, description="Ticker or None for all")


class ScrapeJobCreate(ScrapeJobBase):
    """Schema for creating scrape job."""
    schedule: Optional[str] = Field(None, max_length=100, description="Cron expression")
    is_active: bool = Field(True, description="Whether job is active")
    config: Optional[str] = Field(None, description="JSON configuration")


class ScrapeJobUpdate(BaseModel):
    """Schema for updating scrape job."""
    is_active: Optional[bool] = Field(None, description="Activate or deactivate job")
    last_run: Optional[datetime] = Field(None, description="Last execution time")
    next_run: Optional[datetime] = Field(None, description="Next execution time")
    config: Optional[str] = Field(None, description="JSON configuration")


class ScrapeJobRead(ScrapeJobBase):
    """Schema for reading scrape job."""
    id: int
    schedule: Optional[str]
    is_active: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    config: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class SchedulerStatus(BaseModel):
    """Schema for scheduler status."""
    running: bool = Field(..., description="Whether scheduler is running")
    jobs_count: int = Field(..., description="Number of active jobs")
    last_scrape: Optional[datetime] = Field(None, description="Last scrape execution time")
    next_scrape: Optional[datetime] = Field(None, description="Next scheduled scrape time")


class ManualScrapeRequest(BaseModel):
    """Schema for manual scrape request."""
    days_back: int = Field(7, ge=1, le=365, description="Days to look back")
    max_filings: int = Field(10, ge=1, le=100, description="Max filings to process")


class ManualScrapeResponse(BaseModel):
    """Schema for manual scrape response."""
    ticker: str = Field(..., description="Ticker that was scraped")
    filings_found: int = Field(..., description="Number of filings found")
    trades_created: int = Field(..., description="Number of trades created")
    duration_seconds: float = Field(..., description="Scrape duration")
    status: str = Field(..., description="Success or error status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
