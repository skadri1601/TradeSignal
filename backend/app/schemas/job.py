"""
Pydantic schemas for Job and JobApplication models.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional


# Job Schemas


class JobBase(BaseModel):
    """Base job schema."""

    title: str = Field(..., min_length=1, max_length=200, description="Job title")
    department: str = Field(..., min_length=1, max_length=100, description="Department")
    location: str = Field(..., min_length=1, max_length=200, description="Job location")
    employment_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Employment type (Full-time, Part-time, Contract)",
    )
    description: str = Field(..., min_length=10, description="Full job description")
    requirements: str = Field(
        ..., min_length=10, description="Job requirements and qualifications"
    )
    salary_range: Optional[str] = Field(
        None, max_length=100, description="Salary range (e.g., '$80k-$120k')"
    )
    is_active: bool = Field(default=True, description="Whether job posting is active")

    @validator("employment_type")
    def validate_employment_type(cls, v):
        """Validate employment type is one of the allowed values."""
        allowed = ["Full-time", "Part-time", "Contract", "Internship"]
        if v not in allowed:
            raise ValueError(f'employment_type must be one of: {", ".join(allowed)}')
        return v


class JobCreate(JobBase):
    """Schema for creating a new job."""

    pass


class JobUpdate(BaseModel):
    """Schema for updating a job (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    employment_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=10)
    requirements: Optional[str] = Field(None, min_length=10)
    salary_range: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    """Schema for job response."""

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    application_count: int = Field(
        default=0, description="Number of applications for this job"
    )

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for paginated job list."""

    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int


# JobApplication Schemas


class JobApplicationBase(BaseModel):
    """Base job application schema."""

    applicant_name: str = Field(
        ..., min_length=1, max_length=200, description="Applicant's full name"
    )
    applicant_email: EmailStr = Field(..., description="Applicant's email address")
    applicant_phone: Optional[str] = Field(
        None, max_length=50, description="Applicant's phone number"
    )
    cover_letter: str = Field(
        ..., min_length=50, description="Cover letter (minimum 50 characters)"
    )


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating a new job application."""

    pass


class JobApplicationResponse(JobApplicationBase):
    """Schema for job application response."""

    id: int
    job_id: int
    resume_url: Optional[str] = None
    status: str  # pending, reviewing, rejected, accepted
    created_at: datetime
    updated_at: datetime

    # Include job details
    job_title: Optional[str] = None
    job_department: Optional[str] = None

    class Config:
        from_attributes = True


class JobApplicationStatusUpdate(BaseModel):
    """Schema for updating job application status."""

    status: str = Field(
        ..., description="New status (pending, reviewing, rejected, accepted)"
    )

    @validator("status")
    def validate_status(cls, v):
        """Validate status is one of the allowed values."""
        allowed = ["pending", "reviewing", "rejected", "accepted"]
        if v not in allowed:
            raise ValueError(f'status must be one of: {", ".join(allowed)}')
        return v


class JobApplicationListResponse(BaseModel):
    """Schema for paginated job application list."""

    applications: list[JobApplicationResponse]
    total: int
    page: int
    page_size: int
