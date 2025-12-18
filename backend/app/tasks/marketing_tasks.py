"""
Celery tasks for marketing automation.
"""

import asyncio
import logging
import httpx
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.celery_app import celery_app
from app.config import settings
from app.database import db_manager
from app.models.marketing_campaign import CampaignEmail

logger = logging.getLogger(__name__)


@celery_app.task(name="send_campaign_email")
def send_campaign_email_task(
    email_to: str,
    subject: str,
    html_body: str,
    campaign_id: int,
    campaign_email_id: int,
):
    """Celery task to send a marketing campaign email."""
    async def _async_task():
        if not settings.email_api_key or not settings.email_from:
            logger.warning("Email configuration is missing. Skipping campaign email.")
            return {"status": "skipped", "error": "Email not configured"}

        try:
            payload = {
                "personalizations": [{"to": [{"email": email_to}]}],
                "from": {
                    "email": settings.email_from,
                    "name": settings.email_from_name,
                },
                "subject": subject,
                "content": [{"type": "text/html", "value": html_body}],
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.email_api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()

            # Update campaign email record
            from sqlalchemy import select
            async with db_manager.get_session() as db:
                result = await db.execute(
                    select(CampaignEmail).where(CampaignEmail.id == campaign_email_id)
                )
                campaign_email = result.scalar_one_or_none()
                if campaign_email:
                    # Email sent successfully (already recorded in CampaignEmail.sent_at)
                    logger.info(
                        f"Campaign email {campaign_email_id} sent successfully to {email_to}"
                    )
                else:
                    logger.warning(f"Campaign email {campaign_email_id} not found after sending")

            return {"status": "success", "campaign_email_id": campaign_email_id}

        except httpx.HTTPStatusError as e:
            logger.error(f"SendGrid returned status {e.response.status_code}: {e.response.text[:200]}")
            
            # Mark as bounced
            from sqlalchemy import select
            async with db_manager.get_session() as db:
                result = await db.execute(
                    select(CampaignEmail).where(CampaignEmail.id == campaign_email_id)
                )
                campaign_email = result.scalar_one_or_none()
                if campaign_email:
                    campaign_email.bounced = True
                    await db.commit()

            return {"status": "error", "error": str(e)}
        except Exception as e:
            logger.error(f"Error sending campaign email: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    return asyncio.run(_async_task())


@celery_app.task(name="process_drip_campaign")
def process_drip_campaign_task(campaign_id: int):
    """Process a drip campaign and send scheduled emails."""
    async def _async_task():
        from app.services.marketing_service import MarketingService
        from app.models.marketing_campaign import MarketingCampaign, CampaignStatus
        from sqlalchemy import select
        from app.database import db_manager

        async with db_manager.get_session() as db:
            # Get campaign
            result = await db.execute(
                select(MarketingCampaign).where(MarketingCampaign.id == campaign_id)
            )
            campaign = result.scalar_one_or_none()

            if not campaign or campaign.status != CampaignStatus.ACTIVE.value:
                logger.warning(f"Campaign {campaign_id} is not active")
                return {"status": "skipped", "reason": "campaign_not_active"}

            marketing_service = MarketingService(db)

            # Get recipients
            recipients = await marketing_service.get_campaign_recipients(campaign)

            # Get template
            if not campaign.template_id:
                logger.error(f"Campaign {campaign_id} has no template")
                return {"status": "error", "error": "no_template"}

            template = await marketing_service.get_template(campaign.template_id)
            if not template:
                logger.error(f"Template {campaign.template_id} not found")
                return {"status": "error", "error": "template_not_found"}

            # Send emails to recipients
            sent_count = 0
            for user in recipients:
                try:
                    await marketing_service.send_campaign_email(
                        campaign_id=campaign_id,
                        user_id=user.id,
                        template=template,
                        variables={"user_name": user.username or "User"},
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending email to user {user.id}: {e}")

            logger.info(f"Processed drip campaign {campaign_id}: sent {sent_count} emails")
            return {"status": "success", "sent_count": sent_count}

    return asyncio.run(_async_task())

