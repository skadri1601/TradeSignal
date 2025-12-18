"""
Trade API endpoints.

REST API routes for trade operations.
"""

import logging
from typing import List
from datetime import datetime, timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db, db_manager
from app.services import TradeService, trade_event_manager
from app.services.tier_service import TierService
from app.models.user import User
from app.core.security import get_current_active_user, decode_token
from app.schemas.trade import (
    TradeRead,
    TradeCreate,
    TradeUpdate,
    TradeWithDetails,
    TradeFilter,
    TradeStats,
)
from app.schemas.common import PaginationParams, SortParams, PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.websocket("/stream")
async def trade_stream(websocket: WebSocket):
    """
    WebSocket endpoint streaming trade events in real time.

    Requires Plus tier or higher for real-time updates.
    Pass authentication token as query parameter: ?token=YOUR_TOKEN
    """
    # Accept connection first to send error message if needed
    await websocket.accept()

    # Check authentication and tier
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")

        if not token:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Authentication required. Pass token as query parameter: ?token=YOUR_TOKEN",
                }
            )
            await websocket.close()
            return

        # Verify token and get user
        try:
            payload = decode_token(token)
            user_id_str = payload.get("sub")

            if not user_id_str:
                raise HTTPException(status_code=401, detail="Invalid token")

            user_id = int(user_id_str)
        except Exception:
            await websocket.send_json(
                {"type": "error", "message": "Invalid authentication token"}
            )
            await websocket.close()
            return

        # Check real-time access
        async with db_manager.get_session() as db:
            await TierService.check_real_time_access(user_id, db)

        # User has access, proceed with connection
        await trade_event_manager.connect(websocket)
        await websocket.send_json({"type": "connection_ack"})

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await trade_event_manager.disconnect(websocket)
        except Exception:  # pragma: no cover - defensive cleanup
            await trade_event_manager.disconnect(websocket)

    except HTTPException as e:
        await websocket.send_json({"type": "error", "message": e.detail})
        await websocket.close()
    except Exception as e:
        logger.error(f"Error in trade stream WebSocket: {e}")
        await websocket.send_json({"type": "error", "message": "Internal server error"})
        await websocket.close()


@router.get("/", response_model=PaginatedResponse[TradeWithDetails])
@limiter.limit("60/minute")
async def get_trades(
    request: Request,
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: TradeFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all trades with pagination, filtering, and sorting.

    **Query Parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - sort_by: Field to sort by (default: transaction_date)
    - order: Sort order - asc or desc (default: desc)

    **Filters:**
    - company_id: Filter by company
    - insider_id: Filter by insider
    - ticker: Filter by stock ticker
    - transaction_type: BUY or SELL
    - transaction_date_from: Start date
    - transaction_date_to: End date
    - min_value: Minimum trade value
    - max_value: Maximum trade value
    - significant_only: Only trades >$100k
    """
    # Enforce historical data days restriction
    if filters.transaction_date_from:
        # Calculate days between from_date and today
        from_date = (
            datetime.fromisoformat(filters.transaction_date_from).date()
            if isinstance(filters.transaction_date_from, str)
            else filters.transaction_date_from
        )
        today = datetime.now().date()
        requested_days = (today - from_date).days

        if requested_days > 0:
            max_allowed_days = await TierService.check_historical_data_access(
                current_user.id, requested_days, db
            )
            if max_allowed_days != -1 and requested_days > max_allowed_days:
                # Adjust the from_date to the max allowed
                max_allowed_date = today - timedelta(days=max_allowed_days)
                filters.transaction_date_from = max_allowed_date.isoformat()

    trades, total = await TradeService.get_all(
        db=db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
        sort_by=sort.sort_by,
        order=sort.order,
    )

    return PaginatedResponse.create(
        items=[TradeWithDetails.model_validate(trade) for trade in trades],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get("/recent", response_model=List[TradeWithDetails])
@limiter.limit("60/minute")
async def get_recent_trades(
    request: Request,
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of trades"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recent trades.

    **Parameters:**
    - days: Number of days to look back (1-90, default: 7)
    - limit: Maximum trades to return (1-500, default: 100)

    **Note:** Days parameter is limited by your subscription tier (Free: 30 days,
    Plus: 365 days, Pro/Enterprise: unlimited)

    Returns trades from the last N days, sorted by filing date (newest first).
    """
    # Enforce historical data days restriction
    max_allowed_days = await TierService.check_historical_data_access(
        current_user.id, days, db
    )
    if max_allowed_days != -1 and days > max_allowed_days:
        # Cap days to tier limit
        days = max_allowed_days

    trades = await TradeService.get_recent(db=db, days=days, limit=limit)
    return [TradeWithDetails.model_validate(trade) for trade in trades]


@router.get("/stats", response_model=TradeStats)
@limiter.limit("60/minute")
async def get_trade_statistics(
    request: Request,
    filters: TradeFilter = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trade statistics.

    Calculate statistics like:
    - Total trades, buys, sells
    - Total shares and value traded
    - Average trade size
    - Most active company/insider

    **Filters:** Same filters as /trades endpoint
    """
    stats = await TradeService.get_statistics(db=db, filters=filters)
    return stats


@router.get("/significant", response_model=List[TradeWithDetails])
@limiter.limit("60/minute")
async def get_significant_trades(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of trades"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get significant trades (high value).

    Returns trades above the significance threshold, sorted by filing date (newest first).

    **Parameters:**
    - limit: Maximum trades to return (1-500, default: 100)
    """
    filters = TradeFilter(significant_only=True)
    trades, _ = await TradeService.get_all(
        db=db,
        skip=0,
        limit=limit,
        filters=filters,
        sort_by="filing_date",
        order="desc",
    )
    return [TradeWithDetails.model_validate(trade) for trade in trades]


@router.get("/{trade_id}", response_model=TradeWithDetails)
@limiter.limit("60/minute")
async def get_trade(
    request: Request, trade_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a single trade by ID.

    Returns detailed trade information including company and insider details.
    """
    trade = await TradeService.get_by_id(db=db, trade_id=trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found",
        )

    return TradeWithDetails.model_validate(trade)


@router.post("/", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_trade(
    request: Request, trade_data: TradeCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new trade.

    **Required Fields:**
    - transaction_date: Date of transaction
    - filing_date: Date filed with SEC
    - transaction_type: BUY or SELL
    - shares: Number of shares

    **Optional Fields:**
    - insider_id, company_id, price_per_share, etc.

    **Note:** Checks for duplicates before creating.
    """
    # Check for duplicate (if insider_id is provided)
    if trade_data.insider_id:
        is_duplicate = await TradeService.check_duplicate(
            db=db,
            insider_id=trade_data.insider_id,
            transaction_date=trade_data.transaction_date,
            shares=trade_data.shares,
            price_per_share=trade_data.price_per_share,
        )

        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trade with same insider, date, and shares already exists",
            )

    trade = await TradeService.create(db=db, trade_data=trade_data)
    return TradeRead.model_validate(trade)


@router.patch("/{trade_id}", response_model=TradeRead)
@limiter.limit("20/minute")
async def update_trade(
    request: Request,
    trade_id: int,
    trade_data: TradeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing trade.

    All fields are optional. Only provided fields will be updated.
    """
    trade = await TradeService.get_by_id(db=db, trade_id=trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found",
        )

    updated_trade = await TradeService.update(db=db, trade=trade, trade_data=trade_data)
    return TradeRead.model_validate(updated_trade)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_trade(
    request: Request, trade_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Delete a trade.

    **Warning:** This action cannot be undone.
    """
    trade = await TradeService.get_by_id(db=db, trade_id=trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found",
        )

    await TradeService.delete(db=db, trade=trade)
    return None
