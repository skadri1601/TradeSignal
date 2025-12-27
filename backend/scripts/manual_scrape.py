"""
Manual Scrape Script - Trigger SEC EDGAR scraping manually to catch up on missing data.

This script can be run manually to scrape insider trades for a specific date range.
Useful for catching up on missed data or testing the scraper.

Usage:
    # Scrape last 10 days
    python scripts/manual_scrape.py --days 10
    
    # Scrape last 30 days (default)
    python scripts/manual_scrape.py
    
    # Scrape specific date range
    python scripts/manual_scrape.py --start-date 2025-12-19 --end-date 2025-12-27
"""

import asyncio
import argparse
import platform
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta, date

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix for Windows async event loop
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def manual_scrape_insider_trades(days_back: int = None, start_date: str = None, end_date: str = None):
    """Manually scrape insider trades from SEC EDGAR."""
    from app.database import db_manager
    from app.services.scraper_service import ScraperService
    from app.models import Company
    from sqlalchemy import select

    logger.info("=" * 80)
    logger.info("Starting Manual Insider Trades Scrape")
    logger.info("=" * 80)

    # Calculate days_back if start_date is provided
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            days_back = (end - start).days + 1
        else:
            days_back = (date.today() - start).days + 1
        logger.info(f"Date range: {start_date} to {end_date or 'today'} ({days_back} days)")
    else:
        days_back = days_back or 30
        logger.info(f"Days back: {days_back}")

    # Load companies from database
    tickers = []
    async with db_manager.get_session() as db:
        result = await db.execute(select(Company).filter(Company.cik.isnot(None)))
        companies = result.scalars().all()
        tickers = [c.ticker for c in companies if c.ticker]
        logger.info(f"Loaded {len(tickers)} companies with CIK from database")

    if not tickers:
        logger.error("No companies found to scrape!")
        return {"success": False, "error": "No companies found"}

    scraper = ScraperService()
    results = {
        "success": [],
        "failed": [],
        "tasks_enqueued": 0,
        "companies_processed": 0
    }

    async with db_manager.get_session() as db:
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"[{i}/{len(tickers)}] Enqueuing scrape for {ticker}...")

            try:
                result = await scraper.scrape_company_trades(
                    db=db,
                    ticker=ticker,
                    days_back=days_back,
                    max_filings=100  # Increased for catch-up scraping
                )

                if result.get("success"):
                    task_id = result.get("task_id")
                    results["success"].append(ticker)
                    results["tasks_enqueued"] += 1
                    results["companies_processed"] += 1
                    logger.info(f"  ✓ Task enqueued: {task_id}")
                else:
                    results["failed"].append(ticker)
                    logger.warning(f"  ✗ FAILED: {result.get('message', 'Unknown')}")

            except ValueError as e:
                # CIK not found - skip this company
                results["failed"].append(ticker)
                logger.warning(f"  ⚠ SKIPPED: {str(e)[:200]}")
            except Exception as e:
                results["failed"].append(ticker)
                logger.error(f"  ✗ ERROR: {str(e)[:200]}")

            # Rate limiting for SEC (10 req/sec limit)
            await asyncio.sleep(0.12)
            await db.commit()

    logger.info("=" * 80)
    logger.info("Manual Insider Trades Scrape Complete")
    logger.info(f"Companies processed: {results['companies_processed']}/{len(tickers)}")
    logger.info(f"Tasks enqueued: {results['tasks_enqueued']}")
    logger.info(f"Successful: {len(results['success'])}, Failed: {len(results['failed'])}")
    logger.info("=" * 80)
    logger.info("NOTE: Tasks are running in background. Check Celery worker logs for progress.")
    logger.info("=" * 80)

    if results["failed"]:
        logger.warning(f"Failed/Skipped companies: {', '.join(results['failed'][:10])}")
        if len(results["failed"]) > 10:
            logger.warning(f"... and {len(results['failed']) - 10} more")

    return results


async def main():
    """Main entry point for manual scrape."""
    parser = argparse.ArgumentParser(
        description="Manual Scrape Script - Trigger SEC EDGAR scraping manually",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape last 10 days
  python scripts/manual_scrape.py --days 10
  
  # Scrape specific date range (Dec 19-27, 2025)
  python scripts/manual_scrape.py --start-date 2025-12-19 --end-date 2025-12-27
  
  # Scrape from a specific date to today
  python scripts/manual_scrape.py --start-date 2025-12-19
        """
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Number of days to look back (default: 30, ignored if --start-date is provided)"
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format (e.g., 2025-12-19)"
    )
    
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date in YYYY-MM-DD format (e.g., 2025-12-27). Defaults to today if not provided."
    )

    args = parser.parse_args()

    # Validate date format if provided
    if args.start_date:
        try:
            datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid start-date format: {args.start_date}. Use YYYY-MM-DD (e.g., 2025-12-19)")
            sys.exit(1)
    
    if args.end_date:
        try:
            datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid end-date format: {args.end_date}. Use YYYY-MM-DD (e.g., 2025-12-27)")
            sys.exit(1)

    start_time = datetime.now()
    logger.info(f"Manual scrape started at {start_time.isoformat()}")
    
    try:
        results = await manual_scrape_insider_trades(
            days_back=args.days,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Manual scrape completed in {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
        if results.get("success") is not False:
            logger.info("✓ Scrape completed successfully!")
        else:
            logger.error("✗ Scrape failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Scrape interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scrape failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

