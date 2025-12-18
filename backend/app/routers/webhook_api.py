"""
Webhook API Router.

Endpoints for managing webhook endpoints and viewing delivery history.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.webhook_service import WebhookService
from app.models.webhook import WebhookEventType, WebhookStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_webhook(
    url: str,
    event_types: Optional[List[str]] = None,
    secret: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a new webhook endpoint.

    Event types: trade_alert, conversion, subscription_updated, user_signed_up, custom
    """
    webhook_service = WebhookService(db)
    webhook = await webhook_service.create_webhook(
        user_id=current_user.id,
        url=url,
        event_types=event_types,
        secret=secret,
    )
    return {
        "id": webhook.id,
        "url": webhook.url,
        "event_types": webhook.event_types,
        "is_active": webhook.is_active,
        "created_at": webhook.created_at.isoformat(),
    }


@router.get("")
async def list_webhooks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all webhooks for the current user."""
    webhook_service = WebhookService(db)
    webhooks = await webhook_service.get_user_webhooks(current_user.id)
    return [
        {
            "id": w.id,
            "url": w.url,
            "event_types": w.event_types,
            "is_active": w.is_active,
            "created_at": w.created_at.isoformat(),
        }
        for w in webhooks
    ]


@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: int,
    status: Optional[WebhookStatus] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get delivery history for a webhook."""
    webhook_service = WebhookService(db)

    # Verify webhook belongs to user
    webhooks = await webhook_service.get_user_webhooks(current_user.id)
    if not any(w.id == webhook_id for w in webhooks):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    deliveries = await webhook_service.get_delivery_history(
        webhook_id=webhook_id,
        status=status,
        limit=limit,
    )
    return [
        {
            "id": d.id,
            "event_type": d.event_type,
            "status": d.status,
            "response_code": d.response_code,
            "attempts": d.attempts,
            "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
            "created_at": d.created_at.isoformat(),
        }
        for d in deliveries
    ]


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Send a test webhook event."""
    webhook_service = WebhookService(db)

    # Verify webhook belongs to user
    webhooks = await webhook_service.get_user_webhooks(current_user.id)
    if not any(w.id == webhook_id for w in webhooks):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    test_payload = {
        "test": True,
        "message": "This is a test webhook from TradeSignal",
    }

    delivery = await webhook_service.deliver_webhook(
        webhook_id=webhook_id,
        event_type="custom",
        payload=test_payload,
    )

    return {
        "delivery_id": delivery.id,
        "status": delivery.status,
        "response_code": delivery.response_code,
    }

