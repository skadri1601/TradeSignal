"""
Pydantic schemas for Contact Submission models.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ContactSubmissionBase(BaseModel):
    """Base contact submission schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Contact name")
    company_name: Optional[str] = Field(
        None, max_length=255, description="Company name (optional)"
    )
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(
        None, max_length=20, description="Phone number (optional)"
    )
    message: str = Field(
        ..., min_length=10, max_length=5000, description="Message content"
    )


class PublicContactSubmissionCreate(ContactSubmissionBase):
    """Schema for creating a public contact submission (no auth required)."""

    pass


class AuthenticatedContactSubmissionCreate(ContactSubmissionBase):
    """Schema for creating an authenticated contact submission."""

    pass


class ContactSubmissionResponse(BaseModel):
    """Schema for contact submission response."""

    id: int
    user_id: Optional[int] = None
    name: str
    company_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    message: str
    is_public: bool
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactSubmissionListResponse(BaseModel):
    """Schema for paginated contact submission list."""

    contacts: list[ContactSubmissionResponse]
    total: int
    page: int
    page_size: int


class ContactSubmissionStatusUpdate(BaseModel):
    """Schema for updating contact submission status."""

    status: str = Field(
        ..., description="New status (new, read, replied)"
    )


class ContactSubmissionFilter(BaseModel):
    """Schema for filtering contact submissions."""

    status: Optional[str] = None
    is_public: Optional[bool] = None
    search: Optional[str] = None  # Search by name or email
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
