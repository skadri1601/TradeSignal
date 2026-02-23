"""
Scheduler Service for automated scraping jobs.

Manages APScheduler for periodic SEC Form 4 scraping.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_manager
from app.models import ScrapeHistory, Company
from app.services.scraper_service import ScraperService
from app.services.congressional_scraper import CongressionalScraperService
from app.config import settings
from sqlalchemy import select

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Manages scheduled scraping jobs using APScheduler.

    Features:
    - Periodic scraping of all companies
    - Manual trigger for specific companies
    - Job status monitoring
    - Scrape history logging
    """

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler(
            timezone=settings.scraper_timezone,
            job_defaults={
                "coalesce": True,  # Combine missed runs
                "max_instances": 1,  # Only one instance of each job at a time
                "misfire_grace_time": 3600,  # Allow 1 hour grace period for missed jobs
            },
        )
        self.scraper_service = ScraperService()
        self.congressional_scraper = CongressionalScraperService()
        self._running = False

    async def start(self) -> None:
        """Start the scheduler with default periodic job."""
        if not self._running:
            logger.info("Starting scheduler...")
            # Start scheduler (this is non-blocking for AsyncIOScheduler)
            self.scheduler.start()
            self._running = True
            logger.info("Scheduler started successfully")

            # Add default job: scrape all companies at configured hours
            if settings.scheduler_enabled:
                self.scheduler.add_job(
                    self.scrape_all_companies,
                    "cron",
                    hour=settings.scraper_schedule_hours,
                    id="periodic_scrape_all",
                    name="Periodic Scrape All Companies",
                    replace_existing=True,
                )
                logger.info(
                    f"Scheduler started with periodic scraping at hours: "
                    f"{settings.scraper_schedule_hours} ({settings.scraper_timezone})"
                )
            else:
                logger.info(
                    "Scheduler started but periodic scraping is disabled (SCHEDULER_ENABLED=false)"
                )

            # Add congressional scraping job (every 6 hours)
            if settings.congressional_scraper_enabled:
                self.scheduler.add_job(
                    self.scrape_congressional_trades,
                    "cron",
                    hour=settings.congressional_scrape_hours,
                    id="periodic_scrape_congressional",
                    name="Periodic Congressional Trade Scrape",
                    replace_existing=True,
                )
                logger.info(
                    f"Congressional scraper scheduled at hours: "
                    f"{settings.congressional_scrape_hours} ({settings.scraper_timezone})"
                )
            else:
                logger.info(
                    "Congressional scraper disabled (CONGRESSIONAL_SCRAPER_ENABLED=false)"
                )
            
            logger.info("Scheduler initialization complete")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if self._running:
            # Use wait=False to prevent blocking on shutdown
            # This allows faster termination
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running and self.scheduler.running

    def get_jobs(self) -> List[Job]:
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()

    async def scrape_all_companies(self) -> None:
        """
        Scrape all companies from watchlist file or database.

        Called by scheduled job. Iterates through companies and scrapes
        recent Form 4 filings while respecting rate limits and last scrape times.
        """
        logger.info("=" * 80)
        logger.info("Starting scheduled scrape of all companies")
        logger.info("=" * 80)

        # Try to load companies from watchlist file first
        import os

        watchlist_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "watchlist_companies.txt"
        )

        tickers = []
        try:
            with open(watchlist_path, "r") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith("#"):
                        tickers.append(line)
            logger.info(f"Loaded {len(tickers)} companies from watchlist file")
        except FileNotFoundError:
            logger.warning(
                f"Watchlist file not found at {watchlist_path}, trying database..."
            )
            # Fallback to database if watchlist doesn't exist
            async with db_manager.get_session() as db:
                result = await db.execute(select(Company))
                companies = result.scalars().all()
                tickers = [company.ticker for company in companies if company.ticker]
                logger.info(f"Loaded {len(tickers)} companies from database")
        except Exception as e:
            logger.error(f"Error reading watchlist file: {e}, trying database...")
            # Fallback to database on error
            async with db_manager.get_session() as db:
                result = await db.execute(select(Company))
                companies = result.scalars().all()
                tickers = [company.ticker for company in companies if company.ticker]
                logger.info(f"Loaded {len(tickers)} companies from database")

        if not tickers:
            logger.warning(
                "No companies found in watchlist or database. Scraping cannot proceed."
            )
            logger.warning(
                "Please seed companies using the seed script or add companies to the database."
            )
            return

        async with db_manager.get_session() as db:
            try:
                logger.info(f"Found {len(tickers)} companies to scrape")

                # Track results
                total_filings = 0
                total_trades = 0
                successful = 0
                failed = 0

                for ticker in tickers:
                    try:
                        # Check if scraped recently (skip if within cooldown period)
                        last_scrape = await self._get_last_successful_scrape(db, ticker)
                        cooldown = timedelta(hours=settings.scraper_cooldown_hours)
                        if (
                            last_scrape
                            and (datetime.now() - last_scrape.completed_at) < cooldown
                        ):
                            logger.info(
                                f"Skipping {ticker} - scraped {last_scrape.completed_at}"
                            )
                            continue

                        # Scrape this company with configured parameters
                        result = await self.scrape_company(
                            ticker,
                            days_back=settings.scraper_days_back,
                            max_filings=settings.scraper_max_filings,
                        )

                        if result["status"] == "success":
                            successful += 1
                            total_filings += result["filings_found"]
                            total_trades += result["trades_created"]
                        else:
                            failed += 1

                    except Exception as e:
                        logger.error(f"Error scraping {ticker}: {e}")
                        failed += 1

                logger.info(
                    f"Scheduled scrape complete: {successful} successful, {failed} failed, "
                    f"{total_filings} filings, {total_trades} trades created"
                )

            except Exception as e:
                logger.error(f"Error in scrape_all_companies: {e}", exc_info=True)

    async def scrape_company(
        self, ticker: str, days_back: int = 7, max_filings: int = 10
    ) -> dict:
        """
        Scrape a specific company and log the result.

        Args:
            ticker: Stock ticker symbol
            days_back: Days to look back
            max_filings: Maximum filings to process

        Returns:
            dict with status, filings_found, trades_created, duration, error_message
        """
        start_time = datetime.now()

        # Create scrape history record
        async with db_manager.get_session() as db:
            history = ScrapeHistory(
                ticker=ticker, started_at=start_time, status="running"
            )
            db.add(history)
            await db.commit()
            await db.refresh(history)
            history_id = history.id

        try:
            # Execute scrape
            # Execute scrape using the scraper service
            async with db_manager.get_session() as scrape_db:
                result = await self.scraper_service.scrape_company_trades(
                    db=scrape_db,
                    ticker=ticker,
                    days_back=days_back,
                    max_filings=max_filings,
                )

            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Determine actual status from scraper result
            scrape_success = result.get("success", False)
            filings_found = result.get("filings_processed", 0)
            trades_created = result.get("trades_created", 0)
            actual_status = "success" if scrape_success else "failed"
            error_message = None if scrape_success else result.get("message")

            # Update history record with real results
            async with db_manager.get_session() as db:
                result_history = await db.get(ScrapeHistory, history_id)
                if result_history:
                    result_history.completed_at = end_time
                    result_history.status = actual_status
                    result_history.filings_found = filings_found
                    result_history.trades_created = trades_created
                    result_history.duration_seconds = duration
                    result_history.error_message = error_message
                    await db.commit()

            logger.info(
                f"Scrape completed for {ticker}: status={actual_status}, "
                f"filings={filings_found}, trades={trades_created}"
            )

            return {
                "status": actual_status,
                "ticker": ticker,
                "filings_found": filings_found,
                "trades_created": trades_created,
                "duration_seconds": duration,
                "error_message": error_message,
            }

        except Exception as e:
            # Log failure
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_msg = str(e)

            async with db_manager.get_session() as db:
                result_history = await db.get(ScrapeHistory, history_id)
                if result_history:
                    result_history.completed_at = end_time
                    result_history.status = "failed"
                    result_history.error_message = error_msg
                    result_history.duration_seconds = duration
                    await db.commit()

            logger.error(f"Failed to scrape {ticker}: {error_msg}")

            return {
                "status": "failed",
                "ticker": ticker,
                "filings_found": 0,
                "trades_created": 0,
                "duration_seconds": duration,
                "error_message": error_msg,
            }

    async def trigger_manual_scrape_all(self) -> dict:
        """
        Manually trigger scrape for all companies (bypasses time checks).

        Returns:
            dict with summary statistics
        """
        logger.info("Manual scrape of all companies triggered")

        async with db_manager.get_session() as db:
            result = await db.execute(select(Company))
            companies = result.scalars().all()

            total_filings = 0
            total_trades = 0
            successful = 0
            failed = 0

            for company in companies:
                try:
                    result = await self.scrape_company(
                        company.ticker, days_back=7, max_filings=10
                    )

                    if result["status"] == "success":
                        successful += 1
                        total_filings += result["filings_found"]
                        total_trades += result["trades_created"]
                    else:
                        failed += 1

                except Exception as e:
                    logger.error(f"Error in manual scrape of {company.ticker}: {e}")
                    failed += 1

        return {
            "companies_scraped": successful,
            "companies_failed": failed,
            "total_filings": total_filings,
            "total_trades": total_trades,
        }

    async def _get_last_successful_scrape(
        self, db: AsyncSession, ticker: str
    ) -> Optional[ScrapeHistory]:
        """Get the most recent successful scrape for a ticker."""
        result = await db.execute(
            select(ScrapeHistory)
            .where(ScrapeHistory.ticker == ticker)
            .where(ScrapeHistory.status == "success")
            .order_by(ScrapeHistory.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def scrape_congressional_trades(self) -> None:
        """
        Scrape congressional trades from Finnhub API.

        Called by scheduled job (every 6 hours).
        """
        logger.info("Starting scheduled congressional trade scrape")

        async with db_manager.get_session() as db:
            try:
                result = await self.congressional_scraper.scrape_congressional_trades(
                    db=db, days_back=settings.congressional_scrape_days_back
                )

                logger.info(
                    f"Congressional scrape complete: "
                    f"{result.get('trades_created', 0)} trades created, "
                    f"{result.get('trades_processed', 0)} processed"
                )

            except Exception as e:
                logger.error(f"Error during scheduled congressional scrape: {e}")


# Global scheduler instance
scheduler_service = SchedulerService()
