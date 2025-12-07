"""
Congresspeople API router.

Endpoints for congressional member data.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Congressperson, CongressionalTrade, User
from app.core.security import get_current_active_user
from app.schemas.congressperson import (
    CongresspersonRead,
    CongresspersonFilter,
)
from app.schemas.congressional_trade import CongressionalTradeWithDetails
from app.schemas.common import PaginationParams, PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CongresspersonRead])
async def get_congresspeople(
    pagination: PaginationParams = Depends(),
    filters: CongresspersonFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all congresspeople with filtering and pagination."""
    try:
        query = select(Congressperson)

        # Apply filters
        if filters.chamber:
            query = query.where(Congressperson.chamber == filters.chamber.upper())

        if filters.state:
            query = query.where(Congressperson.state == filters.state.upper())

        if filters.party:
            query = query.where(Congressperson.party == filters.party.upper())

        if filters.active_only:
            query = query.where(Congressperson.active.is_(True))

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Congressperson.name.ilike(search_term),
                    Congressperson.last_name.ilike(search_term),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply sorting (by name)
        query = query.order_by(Congressperson.last_name, Congressperson.first_name)

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute
        result = await db.execute(query)
        congresspeople = result.scalars().all()

        items = [cp.to_dict() for cp in congresspeople]

        return PaginatedResponse.create(
            items=items, total=total, page=pagination.page, limit=pagination.limit
        )

    except Exception as e:
        logger.error(f"Error fetching congresspeople: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching congresspeople: {str(e)}",
        )


@router.get("/{congressperson_id}", response_model=CongresspersonRead)
async def get_congressperson(
    congressperson_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single congressperson by ID."""
    result = await db.execute(
        select(Congressperson).where(Congressperson.id == congressperson_id)
    )
    congressperson = result.scalar_one_or_none()

    if not congressperson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Congressperson {congressperson_id} not found",
        )

    return congressperson.to_dict()


@router.get(
    "/{congressperson_id}/trades", response_model=List[CongressionalTradeWithDetails]
)
async def get_congressperson_trades(
    congressperson_id: int,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all trades for a specific congressperson."""
    # Verify congressperson exists
    cp_result = await db.execute(
        select(Congressperson).where(Congressperson.id == congressperson_id)
    )
    if not cp_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Congressperson {congressperson_id} not found",
        )

    # Fetch trades
    result = await db.execute(
        select(CongressionalTrade)
        .options(selectinload(CongressionalTrade.company))
        .options(selectinload(CongressionalTrade.congressperson))
        .where(CongressionalTrade.congressperson_id == congressperson_id)
        .order_by(desc(CongressionalTrade.transaction_date))
        .limit(limit)
    )
    trades = result.scalars().all()

    items = []
    for trade in trades:
        trade_dict = trade.to_dict()
        if trade.company:
            trade_dict["company"] = trade.company.to_dict()
        if trade.congressperson:
            trade_dict["congressperson"] = trade.congressperson.to_dict()
        items.append(trade_dict)

    return items


@router.get("/search/by-name")
async def search_congresspeople_by_name(
    name: str = Query(..., min_length=2, description="Name to search for"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Search congresspeople by name (for autocomplete)."""
    try:
        search_term = f"%{name}%"

        result = await db.execute(
            select(Congressperson)
            .where(
                or_(
                    Congressperson.name.ilike(search_term),
                    Congressperson.last_name.ilike(search_term),
                )
            )
            .where(Congressperson.active.is_(True))
            .order_by(Congressperson.last_name, Congressperson.first_name)
            .limit(limit)
        )
        congresspeople = result.scalars().all()

        return [
            {
                "id": cp.id,
                "name": cp.name,
                "display_name": cp.display_name,
                "chamber": cp.chamber,
                "state": cp.state,
                "party": cp.party,
                "party_abbrev": cp.party_abbrev,
            }
            for cp in congresspeople
        ]

    except Exception as e:
        logger.error(f"Error searching congresspeople: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )
