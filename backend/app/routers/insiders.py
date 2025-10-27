"""
Insider API endpoints.

REST API routes for insider operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import InsiderService, TradeService
from app.schemas.insider import (
    InsiderRead,
    InsiderCreate,
    InsiderUpdate,
    InsiderWithCompany,
)
from app.schemas.trade import TradeRead, TradeFilter
from app.schemas.common import PaginationParams, SortParams, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[InsiderRead])
async def get_insiders(
    pagination: PaginationParams = Depends(),
    company_id: int | None = Query(None, description="Filter by company"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all insiders with pagination.

    **Query Parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - company_id: Filter by company (optional)

    Returns list of insiders sorted by name.
    """
    insiders, total = await InsiderService.get_all(
        db=db,
        skip=pagination.skip,
        limit=pagination.limit,
        company_id=company_id
    )

    return PaginatedResponse.create(
        items=[InsiderRead.model_validate(insider) for insider in insiders],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/search", response_model=PaginatedResponse[InsiderRead])
async def search_insiders(
    q: str = Query(..., min_length=1, description="Search query (name)"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Search insiders by name.

    **Parameters:**
    - q: Search query (searches insider name)
    - page: Page number
    - limit: Items per page

    Example: `/api/v1/insiders/search?q=tim` matches "Tim Cook", "Timothy Apple", etc.
    """
    insiders, total = await InsiderService.search(
        db=db,
        query=q,
        skip=pagination.skip,
        limit=pagination.limit
    )

    return PaginatedResponse.create(
        items=[InsiderRead.model_validate(insider) for insider in insiders],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/{insider_id}", response_model=InsiderRead)
async def get_insider(
    insider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get insider by ID.

    **Parameters:**
    - insider_id: Insider ID

    Returns insider details including associated company.
    """
    insider = await InsiderService.get_by_id(db=db, insider_id=insider_id)

    if not insider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insider with ID {insider_id} not found"
        )

    return InsiderRead.model_validate(insider)


@router.get("/{insider_id}/trades", response_model=PaginatedResponse[TradeRead])
async def get_insider_trades(
    insider_id: int,
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all trades for a specific insider.

    **Parameters:**
    - insider_id: Insider ID
    - page: Page number
    - limit: Items per page
    - sort_by: Field to sort by (default: transaction_date)
    - order: Sort order - asc or desc (default: desc)

    Returns paginated list of trades by this insider.
    """
    # Verify insider exists
    insider = await InsiderService.get_by_id(db=db, insider_id=insider_id)

    if not insider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insider with ID {insider_id} not found"
        )

    # Get trades for this insider
    filters = TradeFilter(insider_id=insider_id)
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


@router.post("/", response_model=InsiderRead, status_code=status.HTTP_201_CREATED)
async def create_insider(
    insider_data: InsiderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new insider.

    **Required Fields:**
    - name: Insider's full name

    **Optional Fields:**
    - title, company_id, relationship
    - is_director, is_officer, is_ten_percent_owner, is_other

    **Note:** Combination of name + company_id must be unique.
    """
    # Check if insider already exists for this company
    if insider_data.company_id:
        existing = await InsiderService.get_by_name_and_company(
            db=db,
            name=insider_data.name,
            company_id=insider_data.company_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insider '{insider_data.name}' already exists for this company"
            )

    insider = await InsiderService.create(db=db, insider_data=insider_data)
    return InsiderRead.model_validate(insider)


@router.patch("/{insider_id}", response_model=InsiderRead)
async def update_insider(
    insider_id: int,
    insider_data: InsiderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing insider.

    All fields are optional. Only provided fields will be updated.
    """
    insider = await InsiderService.get_by_id(db=db, insider_id=insider_id)

    if not insider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insider with ID {insider_id} not found"
        )

    updated_insider = await InsiderService.update(db=db, insider=insider, insider_data=insider_data)
    return InsiderRead.model_validate(updated_insider)


@router.delete("/{insider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insider(
    insider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an insider.

    **Warning:** This will also delete all associated trades (CASCADE).
    This action cannot be undone.
    """
    insider = await InsiderService.get_by_id(db=db, insider_id=insider_id)

    if not insider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insider with ID {insider_id} not found"
        )

    await InsiderService.delete(db=db, insider=insider)
    return None
