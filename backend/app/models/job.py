"""
Job posting model for careers page.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.job_application import JobApplication


class Job(Base):
    """
    Job posting model for TradeSignal careers page.

    Attributes:
        id: Primary key
        title: Job title
        department: Department (e.g., "Engineering", "Marketing")
        location: Job location (e.g., "Remote", "Dallas, TX")
        employment_type: Employment type (e.g., "Full-time", "Part-time", "Contract")
        description: Full job description
        requirements: Job requirements and qualifications
        salary_range: Salary range (e.g., "$80k-$120k") - optional
        is_active: Whether job posting is active
        created_by: User ID of admin who created the job
        created_at: When job was posted
        updated_at: When job was last updated
    """

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    employment_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Full-time, Part-time, Contract
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    salary_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Foreign keys
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title={self.title}, department={self.department})>"
