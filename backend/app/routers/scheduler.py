"""
Scheduler API endpoints.

Provides REST API for managing scheduled scraping jobs.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.services.scheduler_service import scheduler_service
from app.models import ScrapeHistory
from app.schemas.scrape_job import (
    SchedulerStatus,
    ManualScrapeRequest,
    ManualScrapeResponse,
)
from app.schemas.scrape_history import ScrapeHistoryRead, ScrapeStats
from app.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter()


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status(db: AsyncSession = Depends(get_db)):
    """
    Get scheduler status.

    Returns:
        - running: Whether scheduler is active
        - jobs_count: Number of scheduled jobs
        - last_scrape: Most recent scrape completion time
        - next_scrape: Next scheduled scrape time
    """
    is_running = scheduler_service.is_running()
    jobs = scheduler_service.get_jobs()

    # Get last scrape from history
    last_scrape_result = await db.execute(
        select(ScrapeHistory.completed_at)
        .where(ScrapeHistory.status == 'success')
        .order_by(ScrapeHistory.completed_at.desc())
        .limit(1)
    )
    last_scrape = last_scrape_result.scalar_one_or_none()

    # Get next scheduled run
    next_scrape = None
    if jobs:
        next_runs = [job.next_run_time for job in jobs if job.next_run_time]
        if next_runs:
            next_scrape = min(next_runs)

    return SchedulerStatus(
        running=is_running,
        jobs_count=len(jobs),
        last_scrape=last_scrape,
        next_scrape=next_scrape
    )


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_scheduler():
    """
    Start the scheduler.

    Initiates scheduled scraping jobs. Scheduler runs every 6 hours
    scraping all companies in the database.
    """
    if scheduler_service.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduler is already running"
        )

    await scheduler_service.start()

    return {
        "message": "Scheduler started successfully",
        "jobs": len(scheduler_service.get_jobs())
    }


@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_scheduler():
    """
    Stop the scheduler.

    Stops all scheduled scraping jobs. Manual scraping will still work.
    """
    if not scheduler_service.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduler is not running"
        )

    await scheduler_service.stop()

    return {"message": "Scheduler stopped successfully"}


@router.post("/scrape/{ticker}", response_model=ManualScrapeResponse)
async def manual_scrape_company(
    ticker: str,
    request: ManualScrapeRequest = ManualScrapeRequest()
):
    """
    Manually trigger scrape for a specific company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, TSLA)
        days_back: Days to look back (default: 7)
        max_filings: Max filings to process (default: 10)

    Returns:
        Scrape results including filings found and trades created
    """
    ticker = ticker.upper()

    result = await scheduler_service.scrape_company(
        ticker=ticker,
        days_back=request.days_back,
        max_filings=request.max_filings
    )

    return ManualScrapeResponse(**result)


@router.post("/scrape-all", status_code=status.HTTP_202_ACCEPTED)
async def manual_scrape_all():
    """
    Manually trigger scrape for all companies.

    This bypasses the 4-hour cooldown and scrapes all companies immediately.
    Use sparingly to avoid overwhelming the SEC API.

    Returns:
        Summary of scraping results
    """
    result = await scheduler_service.trigger_manual_scrape_all()

    return {
        "message": "Manual scrape completed",
        **result
    }


@router.get("/history", response_model=PaginatedResponse[ScrapeHistoryRead])
async def get_scrape_history(
    pagination: PaginationParams = Depends(),
    ticker: str = None,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scrape history with pagination.

    Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 20, max: 100)
        - ticker: Filter by ticker symbol
        - status: Filter by status (success, failed, running)

    Returns:
        Paginated list of scrape history records
    """
    query = select(ScrapeHistory)

    # Apply filters
    if ticker:
        query = query.where(ScrapeHistory.ticker == ticker.upper())

    if status_filter:
        query = query.where(ScrapeHistory.status == status_filter)

    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    # Get paginated results
    query = query.order_by(ScrapeHistory.created_at.desc())
    query = query.offset(pagination.skip).limit(pagination.limit)

    result = await db.execute(query)
    history_records = result.scalars().all()

    return PaginatedResponse.create(
        items=[ScrapeHistoryRead.model_validate(record) for record in history_records],
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/history/{ticker}", response_model=List[ScrapeHistoryRead])
async def get_company_scrape_history(
    ticker: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scrape history for a specific company.

    Args:
        ticker: Stock ticker symbol
        limit: Number of records to return (default: 10)

    Returns:
        List of scrape history records for the company
    """
    ticker = ticker.upper()

    result = await db.execute(
        select(ScrapeHistory)
        .where(ScrapeHistory.ticker == ticker)
        .order_by(ScrapeHistory.created_at.desc())
        .limit(limit)
    )

    history_records = result.scalars().all()

    if not history_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scrape history found for {ticker}"
        )

    return [ScrapeHistoryRead.model_validate(record) for record in history_records]


@router.get("/stats", response_model=ScrapeStats)
async def get_scrape_stats(db: AsyncSession = Depends(get_db)):
    """
    Get overall scraping statistics.

    Returns:
        - total_scrapes: Total scrape executions
        - success_count: Successful scrapes
        - failed_count: Failed scrapes
        - avg_duration: Average scrape duration in seconds
        - total_filings_found: Total Form 4 filings discovered
        - total_trades_created: Total trades added to database
    """
    # Get total count
    total_result = await db.execute(select(func.count(ScrapeHistory.id)))
    total_scrapes = total_result.scalar_one()

    # Get success count
    success_result = await db.execute(
        select(func.count(ScrapeHistory.id))
        .where(ScrapeHistory.status == 'success')
    )
    success_count = success_result.scalar_one()

    # Get failed count
    failed_result = await db.execute(
        select(func.count(ScrapeHistory.id))
        .where(ScrapeHistory.status == 'failed')
    )
    failed_count = failed_result.scalar_one()

    # Get aggregates
    agg_result = await db.execute(
        select(
            func.avg(ScrapeHistory.duration_seconds).label('avg_duration'),
            func.sum(ScrapeHistory.filings_found).label('total_filings'),
            func.sum(ScrapeHistory.trades_created).label('total_trades')
        )
    )
    agg = agg_result.one()

    return ScrapeStats(
        total_scrapes=total_scrapes,
        success_count=success_count,
        failed_count=failed_count,
        avg_duration=float(agg.avg_duration or 0.0),
        total_filings_found=agg.total_filings or 0,
        total_trades_created=agg.total_trades or 0
    )
