"""
Alert API endpoints for TradeSignal.

Provides CRUD operations for alerts, testing notifications,
and viewing alert history.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertToggle,
    AlertTestNotification,
    AlertHistoryResponse,
    AlertStatsResponse,
)
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new alert.

    - **name**: User-friendly alert name
    - **alert_type**: Type of alert (large_trade, company_watch, insider_role, volume_spike)
    - **ticker**: Optional ticker filter (e.g., NVDA, TSLA)
    - **min_value**: Optional minimum trade value in USD
    - **max_value**: Optional maximum trade value in USD
    - **transaction_type**: Optional filter (BUY or SELL)
    - **insider_roles**: Optional list of insider role filters (CEO, CFO, Director)
    - **notification_channels**: List of channels (webhook, email, push)
    - **webhook_url**: Webhook URL if using webhook channel
    - **email**: Email address if using email channel
    - **is_active**: Whether alert is enabled (default: true)
    """
    service = AlertService(db)
    alert = await service.create_alert(alert_data)
    return alert


@router.get("/", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all alerts with pagination.

    - **page**: Page number (starts at 1)
    - **limit**: Number of items per page (max 100)
    - **is_active**: Optional filter by active status
    """
    service = AlertService(db)
    skip = (page - 1) * limit
    alerts, total = await service.get_alerts(skip=skip, limit=limit, is_active=is_active)

    return PaginatedResponse.create(
        items=alerts,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single alert by ID.
    """
    service = AlertService(db)
    alert = await service.get_alert(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )

    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing alert.

    All fields are optional - only provided fields will be updated.
    """
    service = AlertService(db)
    alert = await service.update_alert(alert_id, alert_data)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )

    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an alert.

    This will also delete all associated alert history (cascade).
    """
    service = AlertService(db)
    deleted = await service.delete_alert(alert_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )

    return None


@router.post("/{alert_id}/toggle", response_model=AlertResponse)
async def toggle_alert(
    alert_id: int,
    toggle_data: AlertToggle,
    db: AsyncSession = Depends(get_db)
):
    """
    Enable or disable an alert.

    - **is_active**: true to enable, false to disable
    """
    service = AlertService(db)
    alert = await service.toggle_alert(alert_id, toggle_data.is_active)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )

    return alert


@router.post("/{alert_id}/test", status_code=status.HTTP_200_OK)
async def test_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test notification for an alert.

    Useful for verifying webhook configuration without waiting for a real trade.
    """
    service = AlertService(db)
    success, error = await service.send_test_notification(alert_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to send test notification"
        )

    return {"message": "Test notification sent successfully"}


@router.get("/history/", response_model=PaginatedResponse[AlertHistoryResponse])
async def list_alert_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    alert_id: int = Query(None, description="Filter by alert ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert trigger history.

    Shows when alerts were triggered, which trades matched,
    and notification delivery status.

    - **page**: Page number (starts at 1)
    - **limit**: Number of items per page (max 100)
    - **alert_id**: Optional filter by specific alert
    """
    service = AlertService(db)
    skip = (page - 1) * limit
    history, total = await service.get_alert_history(
        alert_id=alert_id,
        skip=skip,
        limit=limit
    )

    return PaginatedResponse.create(
        items=history,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/stats/", response_model=AlertStatsResponse)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get alert statistics.

    Returns counts of total alerts, active/inactive alerts,
    notifications sent, and recent delivery metrics.
    """
    service = AlertService(db)
    stats = await service.get_alert_stats()
    return stats
