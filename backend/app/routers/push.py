"""
Push Notification API endpoints for TradeSignal.

Provides endpoints for managing browser push notification subscriptions.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.push_subscription_service import PushSubscriptionService
from app.schemas.push_subscription import (
    PushSubscriptionCreate,
    PushSubscriptionResponse,
    PushSubscriptionDelete,
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/push", tags=["push-notifications"])


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """
    Get VAPID public key for frontend subscription.

    This key is used by the browser to subscribe to push notifications.
    The key is in URL-safe base64 format suitable for the Push API.

    Returns:
        Dictionary with publicKey field
    """
    if not settings.vapid_public_key_base64:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Push notifications not configured",
        )

    return {"publicKey": settings.vapid_public_key_base64}


@router.post("/subscribe", response_model=PushSubscriptionResponse)
async def subscribe_to_push(
    subscription_data: PushSubscriptionCreate, db: AsyncSession = Depends(get_db)
):
    """
    Register a new push subscription.

    Creates or updates a push subscription for the browser.
    If a subscription with the same endpoint exists, it will be updated.

    - **endpoint**: Push service endpoint URL
    - **p256dh_key**: Client public key for encryption (base64)
    - **auth_key**: Authentication secret (base64)
    - **user_agent**: Optional browser/device info
    """
    if not settings.enable_push_notifications:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Push notifications are disabled",
        )

    service = PushSubscriptionService(db)
    subscription = await service.create_subscription(subscription_data)

    logger.info(f"Push subscription created/updated: {subscription.id}")
    return subscription


@router.post("/unsubscribe")
async def unsubscribe_from_push(
    data: PushSubscriptionDelete, db: AsyncSession = Depends(get_db)
):
    """
    Remove a push subscription.

    Deletes the push subscription from the database.
    The browser should also unsubscribe from the push service.

    - **endpoint**: Endpoint URL to unsubscribe
    """
    service = PushSubscriptionService(db)
    deleted = await service.delete_subscription(data.endpoint)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )

    logger.info(f"Push subscription removed: {data.endpoint[:50]}...")
    return {"message": "Subscription removed successfully"}


@router.get("/subscriptions", response_model=list[PushSubscriptionResponse])
async def get_active_subscriptions(db: AsyncSession = Depends(get_db)):
    """
    Get all active push subscriptions.

    Returns a list of all active push subscriptions in the system.
    Useful for debugging and monitoring.
    """
    service = PushSubscriptionService(db)
    subscriptions = await service.get_active_subscriptions()

    return subscriptions
