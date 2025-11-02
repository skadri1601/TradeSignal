"""
Scrape History Model.

Tracks execution history of scraping jobs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func

from app.database import Base


class ScrapeHistory(Base):
    """Model for tracking scrape job execution history."""

    __tablename__ = "scrape_history"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), index=True, nullable=False, comment="Stock ticker symbol")
    started_at = Column(DateTime(timezone=True), nullable=False, comment="When scrape started")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="When scrape completed")
    status = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Status: running, success, failed"
    )
    filings_found = Column(Integer, default=0, comment="Number of Form 4 filings found")
    trades_created = Column(Integer, default=0, comment="Number of trades created in database")
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    duration_seconds = Column(Float, nullable=True, comment="Scrape duration in seconds")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )

    def __repr__(self) -> str:
        return f"<ScrapeHistory(id={self.id}, ticker={self.ticker}, status={self.status})>"
