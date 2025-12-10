"""
SEC Form 4 Scraper Service

Orchestrates fetching Form 4 filings from SEC and saving to database.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.tasks.sec_tasks import scrape_recent_form4_filings, update_cik_for_company_task

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
        company_query = None
        if ticker:
            company_query = select(Company).where(Company.ticker == ticker.upper())
        elif cik:
            company_query = select(Company).where(Company.cik == cik)
        
        company = None
        if company_query:
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
        
        # If CIK is missing, enqueue a task to update it
        if ticker and not current_cik:
            logger.info(f"CIK missing for ticker {ticker}. Enqueuing CIK lookup task.")
            # This task will update the company in DB if found/created
            update_cik_for_company_task.delay(company_id=company_id, ticker=ticker)
            # We can't wait for the CIK, so we'll proceed with known info and let the scraping task handle CIK resolution if needed.
            # For immediate scraping, CIK is preferred. If not available, we rely on the scheduled task.
            # For now, we'll assume a CIK is available or will be found by scheduled tasks.
            # For an on-demand scrape, it's better to tell the user if CIK isn't immediately available.
            raise ValueError("CIK not found for ticker. Please try again later or wait for background CIK update.")

        if not current_cik:
             raise ValueError("CIK is required for scraping.")

        # Enqueue the actual scraping task
        # We must pass enough info to the Celery task without relying on DB session
        company_info = {
            "company_id": company_id,
            "cik": current_cik,
            "ticker": company_ticker or ticker,
            "name": company_name or "Unknown Company" # Fallback name
        }
        task = scrape_recent_form4_filings.delay(company_info)
        
        logger.info(f"Enqueued Form 4 scraping task for {company_ticker or current_cik}. Task ID: {task.id}")

        return {
            "success": True,
            "task_id": task.id,
            "message": f"Scraping initiated for {company_ticker or current_cik}. Check task status with ID: {task.id}",
        }

    # All helper methods for processing filings, ensuring company/insider, creating trades,
    # and marking filings as processed are now handled within app.tasks.sec_tasks.py
    # so they are removed from this service.

