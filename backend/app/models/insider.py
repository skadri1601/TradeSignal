"""
Insider model for TradeSignal.

Represents corporate insiders who file SEC Form 4 transactions.
"""

from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.trade import Trade


class Insider(Base):
    """
    Insider model representing corporate insiders.

    Attributes:
        id: Primary key
        name: Insider's full name
        title: Job title (CEO, CFO, Director, etc.)
        relationship: Relationship to company
        company_id: Foreign key to Company
        is_director: True if person is a board director
        is_officer: True if person is a corporate officer
        is_ten_percent_owner: True if person owns 10%+ of company stock
        is_other: True if relationship is "other"
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "insiders"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Core Fields
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Foreign Key
    company_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Insider Type Flags
    is_director: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_officer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ten_percent_owner: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_other: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    company: Mapped["Company"] = sa_relationship("Company", back_populates="insiders")
    trades: Mapped[List["Trade"]] = sa_relationship(
        "Trade", back_populates="insider", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Insider."""
        return f"<Insider(id={self.id}, name={self.name}, title={self.title})>"

    @property
    def primary_role(self) -> str:
        """Return the primary role of the insider."""
        if self.is_officer and self.title:
            return self.title
        elif self.is_director:
            return "Director"
        elif self.is_ten_percent_owner:
            return "10% Owner"
        elif self.is_other:
            return "Other"
        else:
            return "Unknown"

    @property
    def roles_list(self) -> List[str]:
        """Return list of all roles."""
        roles = []
        if self.is_officer:
            roles.append("Officer")
        if self.is_director:
            roles.append("Director")
        if self.is_ten_percent_owner:
            roles.append("10% Owner")
        if self.is_other:
            roles.append("Other")
        return roles

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "relationship": self.relationship,
            "company_id": self.company_id,
            "is_director": self.is_director,
            "is_officer": self.is_officer,
            "is_ten_percent_owner": self.is_ten_percent_owner,
            "is_other": self.is_other,
            "primary_role": self.primary_role,
            "roles": self.roles_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
