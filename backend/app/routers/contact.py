"""
Contact form API endpoints for authenticated users.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.contact_submission import ContactSubmission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["Contact"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class ContactRequest(BaseModel):
    """Contact form submission schema for authenticated users."""

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
@limiter.limit("5/hour")  # Limit to 5 submissions per hour
async def submit_contact_form(
    request: Request,
    contact_data: ContactRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a contact form message (authenticated users only).

    Stores submission in database with is_public=False and user_id set.
    Visible to super admin and support admins.
    """
    try:
        # Get client IP address
        client_ip = get_remote_address(request)
        
        # Use user's name if not provided, otherwise use provided name
        name = contact_data.name or current_user.full_name or current_user.username
        # Use user's email if not provided, otherwise use provided email
        email = contact_data.email or current_user.email

        # Create contact submission for authenticated user
        contact_submission = ContactSubmission(
            user_id=current_user.id,
            name=name,
            company_name=contact_data.company_name,
            email=email,
            phone=contact_data.phone,
            message=contact_data.message,
            is_public=False,  # Authenticated users are not public
            ip_address=client_ip,
            status="new",
        )

        # Log values before commit for debugging
        logger.info(
            f"Creating authenticated contact submission:"
        )
        logger.info(f"  User ID: {current_user.id}")
        logger.info(f"  Email: {email}")
        logger.info(f"  Name: {name}")
        logger.info(f"  is_public: {contact_submission.is_public}")
        logger.info(f"  user_id: {contact_submission.user_id}")

        db.add(contact_submission)
        await db.commit()
        await db.refresh(contact_submission)

        # Verify the values after commit
        logger.info(
            f"Contact submission created successfully (ID: {contact_submission.id}):"
        )
        logger.info(f"  Verified is_public: {contact_submission.is_public}")
        logger.info(f"  Verified user_id: {contact_submission.user_id}")
        logger.info(f"  Message: {contact_data.message[:200]}...")

        return ContactResponse(
            success=True,
            message="Thank you! Your message has been sent. We'll get back to you within 24 hours.",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing contact form: {e}", exc_info=True)
        logger.error(f"  User ID: {current_user.id if current_user else 'None'}")
        logger.error(f"  Email: {contact_data.email if contact_data else 'None'}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending your message. Please try again later.",
        )
