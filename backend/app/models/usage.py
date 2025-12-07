"""
Usage tracking model for monitoring user API consumption.
"""

from datetime import datetime, date
from sqlalchemy import Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UsageTracking(Base):
    """
    Track daily usage per user for tier limit enforcement.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        date: Date of usage
        ai_requests: Number of AI requests made
        alerts_triggered: Number of alerts triggered
        api_calls: Number of API calls made
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "usage_tracking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Usage counters
    ai_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    alerts_triggered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    companies_viewed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (Index("ix_usage_user_date", "user_id", "date", unique=True),)

    def __repr__(self) -> str:
        return f"<UsageTracking(user_id={self.user_id}, date={self.date}, ai={self.ai_requests})>"
