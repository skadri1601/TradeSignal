"""
Marketing automation service for email campaigns, drip sequences, and conversion tracking.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.marketing_campaign import (
    MarketingCampaign,
    CampaignEmail,
    EmailTemplate,
    ConversionEvent,
    CampaignType,
    CampaignStatus,
)
from app.models.user import User
from app.tasks.marketing_tasks import send_campaign_email_task
from app.config import settings

logger = logging.getLogger(__name__)


class MarketingService:
    """Service for marketing automation and campaign management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_email_template(
        self,
        name: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EmailTemplate:
        """Create a new email template."""
        template = EmailTemplate(
            name=name,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            variables=variables or {},
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        logger.info(f"Created email template: {name}")
        return template

    async def get_template(self, template_id: int) -> Optional[EmailTemplate]:
        """Get an email template by ID."""
        result = await self.db.execute(
            select(EmailTemplate).where(EmailTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_template_by_name(self, name: str) -> Optional[EmailTemplate]:
        """Get an email template by name."""
        result = await self.db.execute(
            select(EmailTemplate).where(EmailTemplate.name == name)
        )
        return result.scalar_one_or_none()

    async def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        template_id: Optional[int] = None,
        target_segment: Optional[Dict[str, Any]] = None,
        schedule: Optional[Dict[str, Any]] = None,
    ) -> MarketingCampaign:
        """Create a new marketing campaign."""
        campaign = MarketingCampaign(
            name=name,
            campaign_type=campaign_type.value,
            status=CampaignStatus.DRAFT.value,
            template_id=template_id,
            target_segment=target_segment or {},
            schedule=schedule or {},
        )
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        logger.info(f"Created marketing campaign: {name}")
        return campaign

    async def activate_campaign(self, campaign_id: int) -> MarketingCampaign:
        """Activate a campaign."""
        result = await self.db.execute(
            select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign.status = CampaignStatus.ACTIVE.value
        campaign.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(campaign)
        logger.info(f"Activated campaign: {campaign.name}")
        return campaign

    async def get_campaign_recipients(
        self, campaign: MarketingCampaign
    ) -> List[User]:
        """Get list of users matching campaign target segment."""
        query = select(User).where(User.is_active == True)

        # Apply segment filters
        segment = campaign.target_segment or {}
        
        # Filter by tier
        if "tier" in segment:
            # Would need to join with subscriptions table
            # For now, return all active users
            pass

        # Filter by signup date
        if "signup_after" in segment:
            signup_date = datetime.fromisoformat(segment["signup_after"])
            query = query.where(User.created_at >= signup_date)

        # Filter by last activity
        if "last_active_before" in segment:
            # Would need to join with analytics_events
            # For now, skip this filter
            pass

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def send_campaign_email(
        self,
        campaign_id: int,
        user_id: int,
        template: EmailTemplate,
        variables: Optional[Dict[str, Any]] = None,
    ) -> CampaignEmail:
        """Send an email as part of a campaign."""
        # Render template with variables
        subject = self._render_template(template.subject, variables or {})
        html_body = self._render_template(template.html_body, variables or {})

        # Create campaign email record
        campaign_email = CampaignEmail(
            campaign_id=campaign_id,
            user_id=user_id,
            template_id=template.id,
            subject=subject,
            sent_at=datetime.utcnow(),
        )
        self.db.add(campaign_email)
        await self.db.commit()
        await self.db.refresh(campaign_email)

        # Get user email
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.email:
            logger.warning(f"User {user_id} has no email address")
            return campaign_email

        # Enqueue email sending task
        send_campaign_email_task.delay(
            email_to=user.email,
            subject=subject,
            html_body=html_body,
            campaign_id=campaign_id,
            campaign_email_id=campaign_email.id,
        )

        logger.info(f"Enqueued campaign email for user {user_id} in campaign {campaign_id}")
        return campaign_email

    async def track_conversion(
        self,
        user_id: Optional[int],
        event_type: str,
        campaign_id: Optional[int] = None,
        source: Optional[str] = None,
        medium: Optional[str] = None,
        referrer: Optional[str] = None,
        conversion_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversionEvent:
        """Track a conversion event."""
        event = ConversionEvent(
            user_id=user_id,
            event_type=event_type,
            campaign_id=campaign_id,
            source=source,
            medium=medium,
            referrer=referrer,
            conversion_value=conversion_value,
            metadata=metadata or {},
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        logger.info(f"Tracked conversion: {event_type} for user {user_id}")
        return event

    async def get_conversion_funnel(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get conversion funnel statistics."""
        query = select(ConversionEvent)

        if start_date:
            query = query.where(ConversionEvent.created_at >= start_date)
        if end_date:
            query = query.where(ConversionEvent.created_at <= end_date)

        result = await self.db.execute(query)
        events = list(result.scalars().all())

        # Group by event type
        funnel = {}
        for event in events:
            event_type = event.event_type
            if event_type not in funnel:
                funnel[event_type] = {
                    "count": 0,
                    "total_value": 0.0,
                    "unique_users": set(),
                }
            funnel[event_type]["count"] += 1
            if event.conversion_value:
                funnel[event_type]["total_value"] += event.conversion_value
            if event.user_id:
                funnel[event_type]["unique_users"].add(event.user_id)

        # Convert sets to counts
        for event_type in funnel:
            funnel[event_type]["unique_users"] = len(funnel[event_type]["unique_users"])

        return funnel

    async def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """Get statistics for a campaign."""
        # Get total emails sent
        result = await self.db.execute(
            select(func.count(CampaignEmail.id)).where(
                CampaignEmail.campaign_id == campaign_id
            )
        )
        total_sent = result.scalar_one() or 0

        # Get opened count
        result = await self.db.execute(
            select(func.count(CampaignEmail.id)).where(
                and_(
                    CampaignEmail.campaign_id == campaign_id,
                    CampaignEmail.opened_at.isnot(None),
                )
            )
        )
        opened = result.scalar_one() or 0

        # Get clicked count
        result = await self.db.execute(
            select(func.count(CampaignEmail.id)).where(
                and_(
                    CampaignEmail.campaign_id == campaign_id,
                    CampaignEmail.clicked_at.isnot(None),
                )
            )
        )
        clicked = result.scalar_one() or 0

        # Get bounced count
        result = await self.db.execute(
            select(func.count(CampaignEmail.id)).where(
                and_(CampaignEmail.campaign_id == campaign_id, CampaignEmail.bounced == True)
            )
        )
        bounced = result.scalar_one() or 0

        # Get unsubscribed count
        result = await self.db.execute(
            select(func.count(CampaignEmail.id)).where(
                and_(
                    CampaignEmail.campaign_id == campaign_id,
                    CampaignEmail.unsubscribed == True,
                )
            )
        )
        unsubscribed = result.scalar_one() or 0

        return {
            "campaign_id": campaign_id,
            "total_sent": total_sent,
            "opened": opened,
            "clicked": clicked,
            "bounced": bounced,
            "unsubscribed": unsubscribed,
            "open_rate": (opened / total_sent * 100) if total_sent > 0 else 0,
            "click_rate": (clicked / total_sent * 100) if total_sent > 0 else 0,
            "bounce_rate": (bounced / total_sent * 100) if total_sent > 0 else 0,
        }

    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template string with variables."""
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
        return rendered

