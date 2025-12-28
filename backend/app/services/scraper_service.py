"""
SEC Form 4 Scraper Service

Orchestrates fetching Form 4 filings from SEC and saving to database.
NOTE: Celery tasks removed - scraping functionality disabled.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service for orchestrating SEC Form 4 scraping operations via Celery tasks.
    """

    def __init__(self):
        """
        Initialize scraper service.
        """
        pass # No direct SECClient needed here anymore

    async def scrape_company_trades(
        self,
        db: AsyncSession,
        ticker: Optional[str] = None,
        cik: Optional[str] = None,
        days_back: int = 30, # No longer directly used by this service, but kept for compatibility with router schema
        max_filings: int = 100, # No longer directly used by this service, but kept for compatibility with router schema
    ) -> Dict[str, Any]:
        """
        Initiate an asynchronous scrape of Form 4 filings for a specific company
        by enqueuing Celery tasks.

        Args:
            db: Database session
            ticker: Company ticker symbol
            cik: Company CIK
            days_back: (Ignored, handled by background task configuration)
            max_filings: (Ignored, handled by background task configuration)

        Returns:
            A message indicating the scraping task has been initiated.
        """
        if not ticker and not cik:
            raise ValueError("Must provide either ticker or CIK")

        company_id: Optional[int] = None
        current_cik: Optional[str] = cik
        company_name: Optional[str] = None
        company_ticker: Optional[str] = ticker

        # Try to find company in DB
        company = None
        if ticker:
            company_query = select(Company).where(Company.ticker == ticker.upper())
            result = await db.execute(company_query)
            company = result.scalar_one_or_none()
        elif cik:
            company_query = select(Company).where(Company.cik == cik)
            result = await db.execute(company_query)
            company = result.scalar_one_or_none()
        
        if company:
            company_id = company.id
            current_cik = company.cik
            company_name = company.name
            company_ticker = company.ticker
            logger.info(f"Found company {company_name} (ID: {company_id}, CIK: {current_cik}) in DB.")
        else:
            logger.warning(f"Company {ticker or cik} not found in DB. Attempting to create or fetch CIK.")
            # For new companies, create a placeholder in DB if needed (or let SEC tasks handle it)
            # For now, we'll proceed and let the SEC tasks resolve company info.
        
        # NOTE: Celery tasks removed - scraping functionality disabled
        if ticker and not current_cik:
            logger.warning(f"CIK missing for ticker {ticker}. Background tasks disabled.")
            raise ValueError("CIK not found for ticker. Background scraping tasks are currently disabled.")

        if not current_cik:
             raise ValueError("CIK is required for scraping.")

        # NOTE: Celery tasks removed - return disabled message
        logger.warning(f"Scraping requested for {company_ticker or current_cik} but background tasks are disabled.")

        return {
            "success": False,
            "task_id": None,
            "message": f"Background scraping tasks are currently disabled. Data for {company_ticker or current_cik} will be available via scheduled jobs.",
        }

    # All helper methods for processing filings, ensuring company/insider, creating trades,
    # and marking filings as processed are now handled within app.tasks.sec_tasks.py
    # so they are removed from this service.

