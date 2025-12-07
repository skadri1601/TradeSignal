"""
Job application model for careers page.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base

if TYPE_CHECKING:
    from app.models.job import Job


class ApplicationStatus(str, enum.Enum):
    """Application status enum."""

    PENDING = "pending"
    REVIEWING = "reviewing"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class JobApplication(Base):
    """
    Job application model for TradeSignal careers page.

    Attributes:
        id: Primary key
        job_id: Foreign key to Job
        applicant_name: Applicant's full name
        applicant_email: Applicant's email address
        applicant_phone: Applicant's phone number (optional)
        resume_url: URL to uploaded resume (optional, for future file upload)
        cover_letter: Cover letter text
        status: Application status (pending, reviewing, rejected, accepted)
        created_at: When application was submitted
        updated_at: When application was last updated
    """

    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Applicant information
    applicant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    applicant_email: Mapped[str] = mapped_column(String(255), nullable=False)
    applicant_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # For future file upload
    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)

    # Application status
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.PENDING,
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="applications")

    def __repr__(self) -> str:
        return (
            f"<JobApplication(id={self.id}, job_id={self.job_id}, "
            f"applicant={self.applicant_name}, status={self.status})>"
        )
