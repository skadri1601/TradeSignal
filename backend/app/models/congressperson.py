"""
Congressperson model for TradeSignal.

Represents members of the US House of Representatives and Senate.
"""

from datetime import datetime
from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.congressional_trade import CongressionalTrade


class Chamber(str, Enum):
    """Congressional chamber enum."""

    HOUSE = "HOUSE"
    SENATE = "SENATE"


class Party(str, Enum):
    """Political party enum."""

    DEMOCRAT = "DEMOCRAT"
    REPUBLICAN = "REPUBLICAN"
    INDEPENDENT = "INDEPENDENT"
    OTHER = "OTHER"


class Congressperson(Base):
    """
    Congressperson model representing members of Congress.

    Attributes:
        id: Primary key
        name: Full name
        first_name: First name
        last_name: Last name
        chamber: HOUSE or SENATE
        state: State they represent (2-letter code)
        district: District number (for House members)
        party: Political party
        office: Office location
        phone: Office phone number
        website: Official website URL
        twitter: Twitter handle
        bioguide_id: Bioguide identifier
        fec_id: FEC identifier
        active: Whether currently serving
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "congresspeople"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Core Fields
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Congressional Info
    chamber: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    district: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # For House members
    party: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Contact Info
    office: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    twitter: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Identifiers
    bioguide_id: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    fec_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Status
    active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    trades: Mapped[List["CongressionalTrade"]] = relationship(
        "CongressionalTrade",
        back_populates="congressperson",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Congressperson."""
        return f"<Congressperson(id={self.id}, name={self.name}, chamber={self.chamber}, state={self.state})>"

    @property
    def display_name(self) -> str:
        """Return formatted display name with title."""
        title = "Rep." if self.chamber == Chamber.HOUSE.value else "Sen."
        district_info = (
            f" ({self.state}-{self.district})" if self.district else f" ({self.state})"
        )
        return f"{title} {self.name}{district_info}"

    @property
    def party_abbrev(self) -> str:
        """Return party abbreviation."""
        if self.party == Party.DEMOCRAT.value:
            return "D"
        elif self.party == Party.REPUBLICAN.value:
            return "R"
        elif self.party == Party.INDEPENDENT.value:
            return "I"
        else:
            return "O"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "chamber": self.chamber,
            "state": self.state,
            "district": self.district,
            "party": self.party,
            "office": self.office,
            "phone": self.phone,
            "website": self.website,
            "twitter": self.twitter,
            "bioguide_id": self.bioguide_id,
            "fec_id": self.fec_id,
            "active": self.active,
            "display_name": self.display_name,
            "party_abbrev": self.party_abbrev,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
