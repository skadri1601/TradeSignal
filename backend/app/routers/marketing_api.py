"""
Marketing API Router.

Endpoints for marketing automation, campaign management, and conversion tracking.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import get_current_active_user, get_current_superuser
from app.models.user import User
from app.services.marketing_service import MarketingService
from app.models.marketing_campaign import (
    CampaignType,
    CampaignStatus,
    EmailTemplate,
    MarketingCampaign,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketing", tags=["Marketing"])


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_email_template(
    name: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new email template.

    Requires admin access.
    """
    marketing_service = MarketingService(db)
    template = await marketing_service.create_email_template(
        name=name,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )
    return {
        "id": template.id,
        "name": template.name,
        "subject": template.subject,
        "created_at": template.created_at.isoformat(),
    }


@router.get("/templates")
async def list_email_templates(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all email templates."""
    result = await db.execute(select(EmailTemplate))
    templates = result.scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "subject": t.subject,
            "created_at": t.created_at.isoformat(),
        }
        for t in templates
    ]


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    name: str,
    campaign_type: CampaignType,
    template_id: Optional[int] = None,
    target_segment: Optional[Dict[str, Any]] = None,
    schedule: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new marketing campaign.

    Requires admin access.
    """
    marketing_service = MarketingService(db)
    campaign = await marketing_service.create_campaign(
        name=name,
        campaign_type=campaign_type,
        template_id=template_id,
        target_segment=target_segment,
        schedule=schedule,
    )
    return {
        "id": campaign.id,
        "name": campaign.name,
        "campaign_type": campaign.campaign_type,
        "status": campaign.status,
        "created_at": campaign.created_at.isoformat(),
    }


@router.post("/campaigns/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Activate a marketing campaign."""
    marketing_service = MarketingService(db)
    campaign = await marketing_service.activate_campaign(campaign_id)
    return {
        "id": campaign.id,
        "name": campaign.name,
        "status": campaign.status,
    }


@router.get("/campaigns/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get statistics for a marketing campaign."""
    marketing_service = MarketingService(db)
    stats = await marketing_service.get_campaign_stats(campaign_id)
    return stats


@router.post("/conversions/track")
async def track_conversion(
    event_type: str,
    user_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    source: Optional[str] = None,
    medium: Optional[str] = None,
    referrer: Optional[str] = None,
    conversion_value: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Track a conversion event.

    Can be called with or without authentication.
    If authenticated, user_id is taken from current_user.
    """
    marketing_service = MarketingService(db)
    
    # Use authenticated user if available
    if current_user and not user_id:
        user_id = current_user.id

    event = await marketing_service.track_conversion(
        user_id=user_id,
        event_type=event_type,
        campaign_id=campaign_id,
        source=source,
        medium=medium,
        referrer=referrer,
        conversion_value=conversion_value,
        metadata=metadata,
    )
    return {
        "id": event.id,
        "event_type": event.event_type,
        "created_at": event.created_at.isoformat(),
    }


@router.get("/funnel")
async def get_conversion_funnel(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get conversion funnel statistics.

    Requires admin access.
    """
    marketing_service = MarketingService(db)
    funnel = await marketing_service.get_conversion_funnel(
        start_date=start_date,
        end_date=end_date,
    )
    return funnel

