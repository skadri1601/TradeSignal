"""
Congressional Trades API router.

Endpoints for congressional stock trading data.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.services.congressional_trade_service import CongressionalTradeService
from app.services.congressional_scraper import CongressionalScraperService
from app.core.security import get_current_active_user
from app.schemas.congressional_trade import (
    CongressionalTradeWithDetails,
    CongressionalTradeFilter,
    CongressionalTradeStats,
)
from app.schemas.common import PaginationParams, SortParams, PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CongressionalTradeWithDetails])
async def get_congressional_trades(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: CongressionalTradeFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get congressional trades with filtering and pagination.

    Filters available:
    - congressperson_id: Filter by congressperson
    - company_id: Filter by company
    - ticker: Filter by stock ticker
    - chamber: HOUSE or SENATE
    - state: 2-letter state code
    - party: Political party
    - transaction_type: BUY or SELL
    - owner_type: Self, Spouse, Dependent Child, Joint
    - transaction_date_from/to: Date range
    - min_value/max_value: Amount range
    - significant_only: Show only trades > $100k
    """
    try:
        trades, total = await CongressionalTradeService.get_all(
            db=db,
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters,
            sort_by=sort.sort_by,
            order=sort.order,
        )

        # Convert to response schema
        items = []
        for trade in trades:
            trade_dict = trade.to_dict()
            if trade.company:
                trade_dict["company"] = trade.company.to_dict()
            if trade.congressperson:
                trade_dict["congressperson"] = trade.congressperson.to_dict()
            items.append(trade_dict)

        return PaginatedResponse.create(
            items=items, total=total, page=pagination.page, limit=pagination.limit
        )

    except Exception as e:
        logger.error(f"Error fetching congressional trades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trades: {str(e)}",
        )


@router.get("/recent", response_model=List[CongressionalTradeWithDetails])
async def get_recent_congressional_trades(
    days: int = Query(7, ge=1, le=365, description="Days to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum trades to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent congressional trades."""
    try:
        trades = await CongressionalTradeService.get_recent_trades(
            db=db, days=days, limit=limit
        )

        items = []
        for trade in trades:
            trade_dict = trade.to_dict()
            if trade.company:
                trade_dict["company"] = trade.company.to_dict()
            if trade.congressperson:
                trade_dict["congressperson"] = trade.congressperson.to_dict()
            items.append(trade_dict)

        return items

    except Exception as e:
        logger.error(f"Error fetching recent congressional trades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recent trades: {str(e)}",
        )


@router.get("/stats", response_model=CongressionalTradeStats)
async def get_congressional_trade_stats(
    filters: CongressionalTradeFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregate statistics for congressional trades."""
    try:
        stats = await CongressionalTradeService.get_trade_stats(db=db, filters=filters)
        return stats

    except Exception as e:
        logger.error(f"Error calculating congressional trade stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stats: {str(e)}",
        )


@router.get("/{trade_id}", response_model=CongressionalTradeWithDetails)
async def get_congressional_trade(
    trade_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single congressional trade by ID."""
    trade = await CongressionalTradeService.get_by_id(db, trade_id)

    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Congressional trade {trade_id} not found",
        )

    trade_dict = trade.to_dict()
    if trade.company:
        trade_dict["company"] = trade.company.to_dict()
    if trade.congressperson:
        trade_dict["congressperson"] = trade.congressperson.to_dict()

    return trade_dict


@router.post("/scrape")
async def trigger_congressional_scrape(
    ticker: Optional[str] = Query(None, description="Stock ticker (optional)"),
    chamber: Optional[str] = Query(None, description="HOUSE or SENATE (optional)"),
    days_back: int = Query(60, ge=1, le=365, description="Days to look back"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger manual congressional trade scraping.

    Requires authentication. Scrapes congressional trades from Finnhub API.
    """
    try:
        scraper = CongressionalScraperService()
        result = await scraper.scrape_congressional_trades(
            db=db, ticker=ticker, chamber=chamber, days_back=days_back
        )

        return {
            "success": result.get("success", False),
            "message": f"Scrape complete: {result.get('trades_created', 0)} trades created",
            "details": result,
        }

    except Exception as e:
        logger.error(f"Error during congressional scrape: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scrape failed: {str(e)}",
        )
