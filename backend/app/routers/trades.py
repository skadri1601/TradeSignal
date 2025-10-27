"""
Trade API endpoints.

REST API routes for trade operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import TradeService
from app.schemas.trade import (
    TradeRead,
    TradeCreate,
    TradeUpdate,
    TradeWithDetails,
    TradeFilter,
    TradeStats,
)
from app.schemas.common import PaginationParams, SortParams, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TradeRead])
async def get_trades(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: TradeFilter = Depends(),
    db: AsyncSession = Depends(get_db)
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
    trades, total = await TradeService.get_all(
        db=db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
        sort_by=sort.sort_by,
        order=sort.order
    )

    return PaginatedResponse.create(
        items=[TradeRead.model_validate(trade) for trade in trades],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/recent", response_model=List[TradeRead])
async def get_recent_trades(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of trades"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent trades.

    **Parameters:**
    - days: Number of days to look back (1-90, default: 7)
    - limit: Maximum trades to return (1-500, default: 100)

    Returns trades from the last N days, sorted by transaction date (newest first).
    """
    trades = await TradeService.get_recent(db=db, days=days, limit=limit)
    return [TradeRead.model_validate(trade) for trade in trades]


@router.get("/stats", response_model=TradeStats)
async def get_trade_statistics(
    filters: TradeFilter = Depends(),
    db: AsyncSession = Depends(get_db)
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


@router.get("/{trade_id}", response_model=TradeRead)
async def get_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single trade by ID.

    Returns detailed trade information including company and insider details.
    """
    trade = await TradeService.get_by_id(db=db, trade_id=trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found"
        )

    return TradeRead.model_validate(trade)


@router.post("/", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
async def create_trade(
    trade_data: TradeCreate,
    db: AsyncSession = Depends(get_db)
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
            price_per_share=trade_data.price_per_share
        )

        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trade with same insider, date, and shares already exists"
            )

    trade = await TradeService.create(db=db, trade_data=trade_data)
    return TradeRead.model_validate(trade)


@router.patch("/{trade_id}", response_model=TradeRead)
async def update_trade(
    trade_id: int,
    trade_data: TradeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing trade.

    All fields are optional. Only provided fields will be updated.
    """
    trade = await TradeService.get_by_id(db=db, trade_id=trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found"
        )

    updated_trade = await TradeService.update(db=db, trade=trade, trade_data=trade_data)
    return TradeRead.model_validate(updated_trade)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a trade.

    **Warning:** This action cannot be undone.
    """
    trade = await TradeService.get_by_id(db=db, trade_id=trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found"
        )

    await TradeService.delete(db=db, trade=trade)
    return None
