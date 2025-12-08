"""
Contact submission model for TradeSignal.

Handles both public (unauthenticated) and authenticated user contact form submissions.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ContactSubmission(Base):
    """
    Contact form submission model.

    Stores contact form submissions from both public users and authenticated users.
    - Public submissions: is_public=True, user_id=None
    - Authenticated submissions: is_public=False, user_id set

    Attributes:
        id: Primary key
        user_id: Foreign key to users table (optional, only for authenticated users)
        name: Submitter's full name
        company_name: Company name (optional)
        email: Contact email
        phone: Phone number (optional)
        message: Message content
        is_public: Whether this is a public (unauthenticated) submission
        ip_address: IP address for spam prevention
        status: Status of the submission (new, read, replied)
        created_at: Submission timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "contact_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User relationship (optional - only for authenticated users)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    
    # Contact information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 max length
    status: Mapped[str] = mapped_column(
        String(20), default="new", nullable=False, index=True
    )  # new, read, replied
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", backref="contact_submissions")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_contact_public", "is_public", "created_at"),
        Index("idx_contact_user", "user_id", "created_at"),
        Index("idx_contact_status", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ContactSubmission(id={self.id}, email={self.email}, is_public={self.is_public})>"
