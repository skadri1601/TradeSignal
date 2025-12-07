"""
Pydantic schemas for Congressperson model.

Handles request/response validation and serialization for Congress members.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.congressperson import Chamber, Party


class CongresspersonBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., max_length=255, description="Full name")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: str = Field(..., max_length=100, description="Last name")
    chamber: str = Field(..., description="HOUSE or SENATE")
    state: str = Field(..., max_length=2, description="State (2-letter code)")
    district: Optional[str] = Field(
        None, max_length=10, description="District number (House members only)"
    )
    party: str = Field(..., description="Political party")
    office: Optional[str] = Field(None, max_length=255, description="Office location")
    phone: Optional[str] = Field(None, max_length=20, description="Office phone")
    website: Optional[str] = Field(None, max_length=255, description="Official website")
    twitter: Optional[str] = Field(None, max_length=100, description="Twitter handle")
    bioguide_id: Optional[str] = Field(None, max_length=20, description="Bioguide ID")
    fec_id: Optional[str] = Field(None, max_length=20, description="FEC ID")
    active: bool = Field(True, description="Currently serving")

    @field_validator("chamber")
    @classmethod
    def validate_chamber(cls, v: str) -> str:
        """Validate chamber is HOUSE or SENATE."""
        v = v.upper().strip()
        if v not in [Chamber.HOUSE.value, Chamber.SENATE.value]:
            raise ValueError("chamber must be 'HOUSE' or 'SENATE'")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate and uppercase state code."""
        v = v.upper().strip()
        if len(v) != 2:
            raise ValueError("state must be a 2-letter code")
        return v

    @field_validator("party")
    @classmethod
    def validate_party(cls, v: str) -> str:
        """Validate party."""
        v = v.upper().strip()
        valid_parties = [
            Party.DEMOCRAT.value,
            Party.REPUBLICAN.value,
            Party.INDEPENDENT.value,
            Party.OTHER.value,
        ]
        if v not in valid_parties:
            raise ValueError(f"party must be one of: {', '.join(valid_parties)}")
        return v


class CongresspersonCreate(CongresspersonBase):
    """Schema for creating a new congressperson."""

    pass


class CongresspersonUpdate(BaseModel):
    """Schema for updating a congressperson (all fields optional)."""

    name: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    chamber: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    district: Optional[str] = Field(None, max_length=10)
    party: Optional[str] = None
    office: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    twitter: Optional[str] = Field(None, max_length=100)
    bioguide_id: Optional[str] = Field(None, max_length=20)
    fec_id: Optional[str] = Field(None, max_length=20)
    active: Optional[bool] = None

    @field_validator("chamber")
    @classmethod
    def validate_chamber(cls, v: Optional[str]) -> Optional[str]:
        """Validate chamber."""
        if v:
            v = v.upper().strip()
            if v not in [Chamber.HOUSE.value, Chamber.SENATE.value]:
                raise ValueError("chamber must be 'HOUSE' or 'SENATE'")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        """Validate state code."""
        if v:
            v = v.upper().strip()
            if len(v) != 2:
                raise ValueError("state must be a 2-letter code")
        return v

    @field_validator("party")
    @classmethod
    def validate_party(cls, v: Optional[str]) -> Optional[str]:
        """Validate party."""
        if v:
            v = v.upper().strip()
            valid_parties = [
                Party.DEMOCRAT.value,
                Party.REPUBLICAN.value,
                Party.INDEPENDENT.value,
                Party.OTHER.value,
            ]
            if v not in valid_parties:
                raise ValueError(f"party must be one of: {', '.join(valid_parties)}")
        return v


class CongresspersonRead(CongresspersonBase):
    """Schema for reading congressperson data (includes id and timestamps)."""

    id: int = Field(..., description="Congressperson ID")
    display_name: str = Field(..., description="Formatted display name with title")
    party_abbrev: str = Field(..., description="Party abbreviation (D, R, I, O)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CongresspersonFilter(BaseModel):
    """Schema for congressperson filtering parameters."""

    chamber: Optional[str] = Field(None, description="Filter by HOUSE or SENATE")
    state: Optional[str] = Field(None, max_length=2, description="Filter by state")
    party: Optional[str] = Field(None, description="Filter by party")
    active_only: Optional[bool] = Field(True, description="Show only active members")
    search: Optional[str] = Field(None, description="Search by name")

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        """Validate and uppercase state code."""
        if v:
            return v.upper().strip()
        return v
