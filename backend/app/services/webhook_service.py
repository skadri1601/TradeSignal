"""
Webhook service for delivering events to external endpoints.
"""

import logging
import hmac
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import httpx

from app.models.webhook import WebhookEndpoint, WebhookDelivery, WebhookEventType, WebhookStatus
from app.config import settings

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing webhook deliveries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_webhook(
        self,
        user_id: int,
        url: str,
        event_types: Optional[List[str]] = None,
        secret: Optional[str] = None,
    ) -> WebhookEndpoint:
        """Create a new webhook endpoint."""
        webhook = WebhookEndpoint(
            user_id=user_id,
            url=url,
            secret=secret,
            event_types=event_types or [],
            is_active=True,
        )
        self.db.add(webhook)
        await self.db.commit()
        await self.db.refresh(webhook)
        logger.info(f"Created webhook endpoint {webhook.id} for user {user_id}")
        return webhook

    async def get_user_webhooks(self, user_id: int) -> List[WebhookEndpoint]:
        """Get all webhooks for a user."""
        result = await self.db.execute(
            select(WebhookEndpoint).where(WebhookEndpoint.user_id == user_id)
        )
        return list(result.scalars().all())

    async def deliver_webhook(
        self,
        webhook_id: int,
        event_type: str,
        payload: Dict[str, Any],
    ) -> WebhookDelivery:
        """Deliver a webhook event."""
        # Get webhook endpoint
        result = await self.db.execute(
            select(WebhookEndpoint).where(WebhookEndpoint.id == webhook_id)
        )
        webhook = result.scalar_one_or_none()
        if not webhook or not webhook.is_active:
            raise ValueError(f"Webhook {webhook_id} not found or inactive")

        # Check if webhook subscribes to this event type
        if webhook.event_types and event_type not in webhook.event_types:
            logger.debug(f"Webhook {webhook_id} does not subscribe to {event_type}")
            raise ValueError(f"Webhook does not subscribe to {event_type}")

        # Create delivery record
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event_type=event_type,
            payload=payload,
            status=WebhookStatus.PENDING.value,
        )
        self.db.add(delivery)
        await self.db.commit()
        await self.db.refresh(delivery)

        # Deliver webhook
        try:
            # Add timestamp to payload
            payload_with_timestamp = {
                **payload,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
            }

            # Generate signature if secret is set
            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                signature = self._generate_signature(
                    json.dumps(payload_with_timestamp), webhook.secret
                )
                headers["X-Webhook-Signature"] = signature

            # Send webhook
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    json=payload_with_timestamp,
                    headers=headers,
                )
                response.raise_for_status()

            # Update delivery record
            delivery.status = WebhookStatus.SUCCESS.value
            delivery.response_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit response body size
            delivery.delivered_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"Webhook {webhook_id} delivered successfully (delivery {delivery.id})")
            return delivery

        except httpx.HTTPStatusError as e:
            delivery.status = WebhookStatus.FAILED.value
            delivery.response_code = e.response.status_code
            delivery.response_body = e.response.text[:1000]
            await self.db.commit()
            logger.error(f"Webhook {webhook_id} delivery failed: {e.response.status_code}")
            return delivery

        except Exception as e:
            delivery.status = WebhookStatus.FAILED.value
            await self.db.commit()
            logger.error(f"Webhook {webhook_id} delivery error: {e}", exc_info=True)
            return delivery

    async def deliver_event_to_all(
        self,
        event_type: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None,
    ) -> List[WebhookDelivery]:
        """Deliver an event to all matching webhooks."""
        query = select(WebhookEndpoint).where(
            and_(
                WebhookEndpoint.is_active == True,
                # Check if webhook subscribes to this event type
                # (event_types is NULL or contains event_type)
            )
        )

        if user_id:
            query = query.where(WebhookEndpoint.user_id == user_id)

        result = await self.db.execute(query)
        webhooks = list(result.scalars().all())

        # Filter webhooks that subscribe to this event type
        matching_webhooks = [
            w for w in webhooks
            if not w.event_types or event_type in w.event_types
        ]

        deliveries = []
        for webhook in matching_webhooks:
            try:
                delivery = await self.deliver_webhook(
                    webhook.id, event_type, payload
                )
                deliveries.append(delivery)
            except Exception as e:
                logger.error(f"Error delivering webhook {webhook.id}: {e}")

        return deliveries

    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    async def get_delivery_history(
        self,
        webhook_id: Optional[int] = None,
        status: Optional[WebhookStatus] = None,
        limit: int = 100,
    ) -> List[WebhookDelivery]:
        """Get webhook delivery history."""
        query = select(WebhookDelivery)

        if webhook_id:
            query = query.where(WebhookDelivery.webhook_id == webhook_id)
        if status:
            query = query.where(WebhookDelivery.status == status.value)

        query = query.order_by(WebhookDelivery.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

