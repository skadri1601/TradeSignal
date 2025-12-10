"""
Alert API endpoints for TradeSignal.

Provides CRUD operations for alerts, testing notifications,
and viewing alert history.
"""

import logging
import json

from typing import Set
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.alert_service import AlertService
from app.services.tier_service import TierService
from app.models.user import User
from app.core.security import get_current_active_user
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertToggle,
    AlertHistoryResponse,
    AlertStatsResponse,
)
from app.schemas.alert_debug import AlertDebugResponse # Import the new schema
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])
limiter = Limiter(key_func=get_remote_address)


# WebSocket connection manager for real-time alerts with user tracking
class AlertConnectionManager:
    def __init__(self):
        # Map of websocket -> user_id for authenticated connections
        self.authenticated_connections: dict[WebSocket, int] = {}
        # Set of unauthenticated connections (for backwards compatibility during migration)
        self.anonymous_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int | None = None):
        """Connect a WebSocket, optionally with user authentication."""
        if user_id:
            self.authenticated_connections[websocket] = user_id
            logger.info(
                f"Alert WebSocket connected for user {user_id}. Auth connections: {len(self.authenticated_connections)}"
            )
        else:
            self.anonymous_connections.add(websocket)
            logger.info(
                f"Alert WebSocket connected (anonymous). Anon connections: {len(self.anonymous_connections)}"
            )

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket from either pool."""
        if websocket in self.authenticated_connections:
            user_id = self.authenticated_connections.pop(websocket)
            logger.info(
                f"Alert WebSocket disconnected for user {user_id}. Auth connections: {len(self.authenticated_connections)}"
            )
        else:
            self.anonymous_connections.discard(websocket)
            logger.info(
                f"Alert WebSocket disconnected (anonymous). Anon connections: {len(self.anonymous_connections)}"
            )

    async def broadcast(self, message: dict, user_id: int | None = None):
        """
        Broadcast alert notification to connected clients.

        If user_id is provided, only send to that user's connections.
        Otherwise, broadcast to all connections (backwards compatible).
        """
        disconnected = []

        if user_id:
            # Send only to specific user's connections
            for websocket, ws_user_id in self.authenticated_connections.items():
                if ws_user_id == user_id:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(
                            f"Failed to send to WebSocket for user {user_id}: {e}"
                        )
                        disconnected.append(websocket)
        else:
            # Broadcast to all authenticated connections
            for websocket in list(self.authenticated_connections.keys()):
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to authenticated WebSocket: {e}")
                    disconnected.append(websocket)

            # Also send to anonymous connections (backwards compatibility)
            for websocket in list(self.anonymous_connections):
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to anonymous WebSocket: {e}")
                    disconnected.append(websocket)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_user(self, user_id: int, message: dict):
        """Send a message to a specific user's connections."""
        await self.broadcast(message, user_id=user_id)

    @property
    def total_connections(self) -> int:
        """Get total number of active connections."""
        return len(self.authenticated_connections) + len(self.anonymous_connections)


alert_manager = AlertConnectionManager()

def get_alert_manager() -> AlertConnectionManager:
    return alert_manager

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_alert(
    request: Request,
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new alert.

    - **name**: User-friendly alert name
    - **alert_type**: Type of alert (large_trade, company_watch, insider_role,
      volume_spike)
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
    try:
        # Check tier limit before creating alert
        await TierService.check_alert_limit(current_user.id, db)

        service = AlertService(db)
        alert = await service.create_alert(alert_data, current_user.id)
        return alert
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )


@router.get("/", response_model=PaginatedResponse[AlertResponse])
@limiter.limit("60/minute")
async def list_alerts(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all alerts with pagination.

    - **page**: Page number (starts at 1)
    - **limit**: Number of items per page (max 100)
    - **is_active**: Optional filter by active status
    """
    service = AlertService(db)
    skip = (page - 1) * limit
    alerts, total = await service.get_alerts(
        skip=skip, limit=limit, is_active=is_active
    )

    return PaginatedResponse.create(items=alerts, total=total, page=page, limit=limit)


@router.get("/{alert_id}", response_model=AlertResponse)
@limiter.limit("60/minute")
async def get_alert(
    request: Request, alert_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a single alert by ID.
    """
    service = AlertService(db)
    alert = await service.get_alert(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found",
        )

    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
@limiter.limit("20/minute")
async def update_alert(
    request: Request,
    alert_id: int,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
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
            detail=f"Alert with id {alert_id} not found",
        )

    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_alert(
    request: Request, alert_id: int, db: AsyncSession = Depends(get_db)
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
            detail=f"Alert with id {alert_id} not found",
        )

    return None


@router.post("/{alert_id}/toggle", response_model=AlertResponse)
@limiter.limit("20/minute")
async def toggle_alert(
    request: Request,
    alert_id: int,
    toggle_data: AlertToggle,
    db: AsyncSession = Depends(get_db),
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
            detail=f"Alert with id {alert_id} not found",
        )

    return alert


@router.post("/{alert_id}/test", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def test_alert(
    request: Request, alert_id: int, db: AsyncSession = Depends(get_db)
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
            detail=error or "Failed to send test notification",
        )

    return {"message": "Test notification sent successfully"}


@router.get("/{alert_id}/debug", response_model=AlertDebugResponse)
@limiter.limit("20/minute")
async def debug_alert(
    request: Request, alert_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get detailed debug information for a specific alert.
    Includes alert configuration and recent trigger history.
    """
    service = AlertService(db)
    alert = await service.get_alert(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found",
        )
    
    # Fetch recent alert history for this alert
    history, _ = await service.get_alert_history(alert_id=alert_id, limit=10) # Last 10 entries

    return AlertDebugResponse(
        alert=AlertResponse.model_validate(alert),
        recent_history=[AlertHistoryResponse.model_validate(h) for h in history]
    )

@router.get("/history/", response_model=PaginatedResponse[AlertHistoryResponse])
@limiter.limit("60/minute")
async def list_alert_history(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    alert_id: int = Query(None, description="Filter by alert ID"),
    db: AsyncSession = Depends(get_db),
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
        alert_id=alert_id, skip=skip, limit=limit
    )

    return PaginatedResponse.create(items=history, total=total, page=page, limit=limit)


@router.get("/stats/", response_model=AlertStatsResponse)
@limiter.limit("60/minute")
async def get_alert_stats(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Get alert statistics.

    Returns counts of total alerts, active/inactive alerts,
    notifications sent, and recent delivery metrics.
    """
    service = AlertService(db)
    stats = await service.get_alert_stats()
    return stats


@router.websocket("/stream")
async def alert_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications.

    Supports both authenticated and anonymous connections:
    - Authenticated: Pass token as query parameter: ?token=YOUR_TOKEN
      Only receives alerts for your own alerts.
    - Anonymous: No token required (backwards compatible)
      May receive broadcast alerts.

    Expected message format from server:
    {
        "id": "unique-id",
        "title": "Alert Title",
        "message": "Alert message content",
        "kind": "info|success|warning|error",
        "duration": 6000,
        "meta": {
            "alert_id": 123,
            "trade_id": 456,
            "link": "/alerts/123"
        }
    }
    """
    await websocket.accept()

    user_id: int | None = None

    # Try to authenticate if token is provided
    token = websocket.query_params.get("token")
    if token:
        try:
            from app.core.security import decode_token

            payload = decode_token(token)
            user_id_str = payload.get("sub")

            if user_id_str:
                user_id = int(user_id_str)
                logger.info(f"Alert WebSocket authenticated for user {user_id}")
        except Exception as e:
            logger.warning(f"Alert WebSocket auth failed: {e}")
            # Continue as anonymous connection

    # Connect with or without user_id
    await alert_manager.connect(websocket, user_id=user_id)

    # Send connection acknowledgment
    await websocket.send_json(
        {
            "type": "connection_ack",
            "authenticated": user_id is not None,
            "user_id": user_id,
        }
    )

    try:
        # Keep connection alive and handle incoming messages
        # Notifications will only be sent when alerts are triggered
        while True:
            try:
                data = await websocket.receive_text()
                # Handle ping/pong for keepalive
                if data:
                    msg = json.loads(data)
                    if msg.get("type") == "ping":
                        await websocket.send_json({"type": "pong", "t": msg.get("t")})
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket: {e}")
                break

    finally:
        alert_manager.disconnect(websocket)
