"""
Company API endpoints.

REST API routes for company operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services import CompanyService, TradeService
from app.services.company_enrichment_service import CompanyEnrichmentService
from app.schemas.company import (
    CompanyRead,
    CompanyCreate,
    CompanyUpdate,
    CompanyWithStats,
    CompanySearch,
)
from app.schemas.trade import TradeRead, TradeFilter, TradeWithDetails
from app.schemas.common import PaginationParams, SortParams, PaginatedResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/", response_model=PaginatedResponse[CompanyRead])
@limiter.limit("60/minute")
async def get_companies(
    request: Request,
    pagination: PaginationParams = Depends(),
    sector: str | None = Query(None, description="Filter by sector"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all companies with pagination.

    **Query Parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - sector: Filter by sector (optional)

    Returns list of companies sorted by ticker.
    """
    companies, total = await CompanyService.get_all(
        db=db,
        skip=pagination.skip,
        limit=pagination.limit,
        sector=sector
    )

    return PaginatedResponse.create(
        items=[CompanyRead.model_validate(company) for company in companies],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/search", response_model=PaginatedResponse[CompanyRead])
@limiter.limit("60/minute")
async def search_companies(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query (ticker or name)"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Search companies by ticker or name.

    **Parameters:**
    - q: Search query (searches both ticker and company name)
    - page: Page number
    - limit: Items per page

    Example: `/api/v1/companies/search?q=apple` matches "AAPL" and "Apple Inc."
    """
    companies, total = await CompanyService.search(
        db=db,
        query=q,
        skip=pagination.skip,
        limit=pagination.limit
    )

    return PaginatedResponse.create(
        items=[CompanyRead.model_validate(company) for company in companies],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/{ticker}", response_model=CompanyWithStats)
@limiter.limit("60/minute")
async def get_company_by_ticker(
    request: Request,
    ticker: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get company by ticker symbol with statistics.

    **Parameters:**
    - ticker: Stock ticker (case-insensitive)

    Returns company details with trading statistics:
    - Total trades
    - Total insiders
    - Recent buy/sell counts (last 30 days)

    **Auto-enrichment**: If company details are missing (description, sector, industry),
    they will be automatically fetched from SEC EDGAR on first view.
    """
    company = await CompanyService.get_by_ticker(db=db, ticker=ticker)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker}' not found"
        )

    # Auto-enrich company data if missing details
    enrichment_service = CompanyEnrichmentService(db)
    if not company.description or not company.sector:
        await enrichment_service.enrich_company(company.id)

    company_stats = await CompanyService.get_with_stats(db=db, company_id=company.id)
    return company_stats


@router.get("/{ticker}/trades", response_model=PaginatedResponse[TradeWithDetails])
@limiter.limit("60/minute")
async def get_company_trades(
    request: Request,
    ticker: str,
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all trades for a specific company.

    **Parameters:**
    - ticker: Stock ticker
    - page: Page number
    - limit: Items per page
    - sort_by: Field to sort by (default: transaction_date)
    - order: Sort order - asc or desc (default: desc)

    Returns paginated list of trades for the company.
    """
    # Get company
    company = await CompanyService.get_by_ticker(db=db, ticker=ticker)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker}' not found"
        )

    # Get trades for this company
    filters = TradeFilter(company_id=company.id)
    trades, total = await TradeService.get_all(
        db=db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
        sort_by=sort.sort_by,
        order=sort.order
    )

    return PaginatedResponse.create(
        items=[TradeWithDetails.model_validate(trade) for trade in trades],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_company(
    request: Request,
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new company.

    **Required Fields:**
    - ticker: Stock ticker (will be uppercased)
    - cik: SEC Central Index Key (10 digits)

    **Optional Fields:**
    - name, sector, industry, market_cap, description, website

    **Note:** Ticker and CIK must be unique.
    """
    # Check if company exists
    existing = await CompanyService.get_by_ticker(db=db, ticker=company_data.ticker)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with ticker '{company_data.ticker}' already exists"
        )

    existing_cik = await CompanyService.get_by_cik(db=db, cik=company_data.cik)
    if existing_cik:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with CIK '{company_data.cik}' already exists"
        )

    company = await CompanyService.create(db=db, company_data=company_data)
    return CompanyRead.model_validate(company)


@router.patch("/{ticker}", response_model=CompanyRead)
@limiter.limit("20/minute")
async def update_company(
    request: Request,
    ticker: str,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing company.

    All fields are optional. Only provided fields will be updated.
    """
    company = await CompanyService.get_by_ticker(db=db, ticker=ticker)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker}' not found"
        )

    updated_company = await CompanyService.update(db=db, company=company, company_data=company_data)
    return CompanyRead.model_validate(updated_company)


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_company(
    request: Request,
    ticker: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a company.

    **Warning:** This will also delete all associated insiders and trades (CASCADE).
    This action cannot be undone.
    """
    company = await CompanyService.get_by_ticker(db=db, ticker=ticker)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker}' not found"
        )

    await CompanyService.delete(db=db, company=company)
    return None
