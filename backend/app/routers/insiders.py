"""
Insider API endpoints.

REST API routes for insider operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services import InsiderService, TradeService
from app.services.company_enrichment_service import CompanyEnrichmentService
from app.schemas.insider import (
    InsiderRead,
    InsiderCreate,
    InsiderUpdate,
)
from app.schemas.trade import TradeFilter, TradeWithDetails
from app.schemas.common import PaginationParams, SortParams, PaginatedResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/", response_model=PaginatedResponse[InsiderRead])
@limiter.limit("60/minute")
async def get_insiders(
    request: Request,
    pagination: PaginationParams = Depends(),
    company_id: int | None = Query(None, description="Filter by company"),
    db: AsyncSession = Depends(get_db),
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
        db=db, skip=pagination.skip, limit=pagination.limit, company_id=company_id
    )

    return PaginatedResponse.create(
        items=[InsiderRead.model_validate(insider) for insider in insiders],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get("/search", response_model=PaginatedResponse[InsiderRead])
@limiter.limit("60/minute")
async def search_insiders(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query (name)"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
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
        db=db, query=q, skip=pagination.skip, limit=pagination.limit
    )

    return PaginatedResponse.create(
        items=[InsiderRead.model_validate(insider) for insider in insiders],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get("/{insider_id}", response_model=InsiderRead)
@limiter.limit("60/minute")
async def get_insider(
    request: Request, insider_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get insider by ID.

    **Parameters:**
    - insider_id: Insider ID

    Returns insider details including associated company.

    **Auto-enrichment**: If insider details are missing (title, email),
    they will be automatically fetched from SEC EDGAR on first view.
    """
    insider = await InsiderService.get_by_id(db=db, insider_id=insider_id)

    if not insider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insider with ID {insider_id} not found",
        )

    # Auto-enrich insider data if missing details
    enrichment_service = CompanyEnrichmentService(db)
    if not insider.title:
        await enrichment_service.enrich_insider(insider_id)

    return InsiderRead.model_validate(insider)


@router.get("/{insider_id}/trades", response_model=PaginatedResponse[TradeWithDetails])
@limiter.limit("60/minute")
async def get_insider_trades(
    request: Request,
    insider_id: int,
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    db: AsyncSession = Depends(get_db),
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
            detail=f"Insider with ID {insider_id} not found",
        )

    # Get trades for this insider
    filters = TradeFilter(insider_id=insider_id)
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


@router.post("/", response_model=InsiderRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_insider(
    request: Request, insider_data: InsiderCreate, db: AsyncSession = Depends(get_db)
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
            db=db, name=insider_data.name, company_id=insider_data.company_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insider '{insider_data.name}' already exists for this company",
            )

    insider = await InsiderService.create(db=db, insider_data=insider_data)
    return InsiderRead.model_validate(insider)


@router.patch("/{insider_id}", response_model=InsiderRead)
@limiter.limit("20/minute")
async def update_insider(
    request: Request,
    insider_id: int,
    insider_data: InsiderUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing insider.

    All fields are optional. Only provided fields will be updated.
    """
    insider = await InsiderService.get_by_id(db=db, insider_id=insider_id)

    if not insider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insider with ID {insider_id} not found",
        )

    updated_insider = await InsiderService.update(
        db=db, insider=insider, insider_data=insider_data
    )
    return InsiderRead.model_validate(updated_insider)


@router.delete("/{insider_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_insider(
    request: Request, insider_id: int, db: AsyncSession = Depends(get_db)
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
            detail=f"Insider with ID {insider_id} not found",
        )

    await InsiderService.delete(db=db, insider=insider)
    return None
