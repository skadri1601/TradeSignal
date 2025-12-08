"""
Public contact form API endpoints (no authentication required).
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.contact_submission import ContactSubmission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/contact", tags=["Public Contact"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class PublicContactRequest(BaseModel):
    """Public contact form submission schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    company_name: str | None = Field(
        None, max_length=255, description="Company name (optional)"
    )
    email: EmailStr = Field(..., description="Contact email")
    phone: str | None = Field(None, max_length=20, description="Phone number (optional)")
    message: str = Field(
        ..., min_length=10, max_length=5000, description="Message content"
    )


class ContactResponse(BaseModel):
    """Contact form response."""

    success: bool
    message: str


@router.post("/", response_model=ContactResponse)
@limiter.limit("5/hour")  # Limit to 5 submissions per hour per IP
async def submit_public_contact_form(
    request: Request,
    contact_data: PublicContactRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a public contact form message (no authentication required).

    Stores submission in database with is_public=True.
    Rate limited to 5 submissions per hour per IP address.
    """
    try:
        # Get client IP address for rate limiting and spam prevention
        client_ip = get_remote_address(request)
        
        # Check for recent submissions from same IP (additional spam prevention)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_submissions = await db.execute(
            select(func.count(ContactSubmission.id)).where(
                ContactSubmission.ip_address == client_ip,
                ContactSubmission.created_at >= one_hour_ago
            )
        )
        recent_count = recent_submissions.scalar() or 0
        
        if recent_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many submissions. Please try again later.",
            )

        # Create contact submission
        contact_submission = ContactSubmission(
            name=contact_data.name,
            company_name=contact_data.company_name,
            email=contact_data.email,
            phone=contact_data.phone,
            message=contact_data.message,
            is_public=True,
            ip_address=client_ip,
            status="new",
        )

        db.add(contact_submission)
        await db.commit()
        await db.refresh(contact_submission)

        logger.info(
            f"Public contact form submission from {contact_data.email} (IP: {client_ip}):"
        )
        logger.info(f"  Name: {contact_data.name}")
        logger.info(f"  Message: {contact_data.message[:200]}...")

        return ContactResponse(
            success=True,
            message="Thank you! Your message has been sent. We'll get back to you within 24 hours.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing public contact form: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending your message. Please try again later.",
        )
