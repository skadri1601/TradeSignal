"""
Scrape Job Model.

Tracks scheduled scraping jobs configuration.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.database import Base


class ScrapeJob(Base):
    """Model for scheduled scrape job configurations."""

    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False, comment="APScheduler job ID")
    job_type = Column(
        String(50),
        nullable=False,
        comment="Job type: periodic_scrape, manual_scrape, etc."
    )
    ticker = Column(
        String(10),
        nullable=True,
        index=True,
        comment="Specific ticker or NULL for all companies"
    )
    schedule = Column(String(100), nullable=True, comment="Cron expression for scheduling")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether job is active")
    last_run = Column(DateTime(timezone=True), nullable=True, comment="Last execution time")
    next_run = Column(DateTime(timezone=True), nullable=True, comment="Next scheduled execution")
    config = Column(Text, nullable=True, comment="JSON config for job parameters")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp"
    )

    def __repr__(self) -> str:
        return f"<ScrapeJob(id={self.id}, job_id={self.job_id}, ticker={self.ticker})>"
