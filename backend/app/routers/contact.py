"""
Contact form API endpoints.
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["Contact"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class ContactRequest(BaseModel):
    """Contact form submission schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Contact name")
    email: EmailStr = Field(..., description="Contact email")
    subject: str = Field(
        ..., min_length=1, max_length=255, description="Message subject"
    )
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
    Submit a contact form message.

    Messages are sent to the support email address configured in settings.
    """
    try:
        # In a production environment, you would:
        # 1. Store the message in a database table
        # 2. Send an email to support@tradesignal.com
        # 3. Optionally send a confirmation email to the user

        # For now, we'll log it and return success
        # TODO: Implement email sending via notification service

        # support_email = os.getenv("SUPPORT_EMAIL", "support@tradesignal.com")

        logger.info(
            f"Contact form submission from {contact_data.email} ({current_user.id}):"
        )
        logger.info(f"  Subject: {contact_data.subject}")
        logger.info(f"  Message: {contact_data.message[:200]}...")

        # TODO: Send email to support@tradesignal.com
        # from app.services.notification_service import NotificationService
        # notification_service = NotificationService()
        # await notification_service.send_contact_form_email(
        #     to_email=support_email,
        #     from_email=contact_data.email,
        #     from_name=contact_data.name,
        #     subject=contact_data.subject,
        #     message=contact_data.message,
        #     user_id=current_user.id
        # )

        return ContactResponse(
            success=True,
            message="Thank you! Your message has been sent. We'll get back to you within 24 hours.",
        )
    except Exception as e:
        logger.error(f"Error processing contact form: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending your message. Please try again later.",
        )
