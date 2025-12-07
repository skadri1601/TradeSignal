"""
Push Subscription Service for TradeSignal.

Manages browser push notification subscriptions.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime

from app.models.push_subscription import PushSubscription
from app.schemas.push_subscription import PushSubscriptionCreate

logger = logging.getLogger(__name__)


class PushSubscriptionService:
    """
    Service for managing push notification subscriptions.

    Responsibilities:
    - Register new push subscriptions
    - Remove expired/revoked subscriptions
    - Retrieve active subscriptions for notifications
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription(
        self, data: PushSubscriptionCreate
    ) -> PushSubscription:
        """
        Create or update a push subscription.

        If subscription with same endpoint exists, updates it.
        Otherwise creates a new subscription.

        Args:
            data: Push subscription data from browser

        Returns:
            PushSubscription instance
        """
        # Check if subscription already exists
        result = await self.db.execute(
            select(PushSubscription).where(PushSubscription.endpoint == data.endpoint)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing subscription
            existing.p256dh_key = data.p256dh_key
            existing.auth_key = data.auth_key
            existing.user_agent = data.user_agent
            existing.is_active = True
            existing.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(existing)

            logger.info(f"Updated push subscription: {existing.id}")
            return existing

        # Create new subscription
        subscription = PushSubscription(**data.model_dump())
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        logger.info(f"Created new push subscription: {subscription.id}")
        return subscription

    async def delete_subscription(self, endpoint: str) -> bool:
        """
        Delete a push subscription by endpoint.

        Args:
            endpoint: Push service endpoint URL

        Returns:
            True if subscription was deleted, False if not found
        """
        result = await self.db.execute(
            delete(PushSubscription).where(PushSubscription.endpoint == endpoint)
        )
        await self.db.commit()

        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted push subscription: {endpoint[:50]}...")

        return deleted

    async def get_active_subscriptions(self) -> list[PushSubscription]:
        """
        Get all active push subscriptions.

        Returns:
            List of active PushSubscription instances
        """
        result = await self.db.execute(
            select(PushSubscription).where(PushSubscription.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def mark_subscription_inactive(self, subscription_id: int) -> None:
        """
        Mark a subscription as inactive (e.g., after 410 Gone error).

        Args:
            subscription_id: ID of subscription to deactivate
        """
        subscription = await self.db.get(PushSubscription, subscription_id)
        if subscription:
            subscription.is_active = False
            await self.db.commit()
            logger.info(f"Marked subscription {subscription_id} as inactive")

    async def update_last_notified(self, subscription_id: int) -> None:
        """
        Update the last_notified_at timestamp for a subscription.

        Args:
            subscription_id: ID of subscription to update
        """
        subscription = await self.db.get(PushSubscription, subscription_id)
        if subscription:
            subscription.last_notified_at = datetime.utcnow()
            await self.db.commit()
