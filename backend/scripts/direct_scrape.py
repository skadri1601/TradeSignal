"""
Direct SEC Scraper - Scrapes SEC Form 4 filings directly WITHOUT Celery.

This script bypasses the Celery task queue and writes directly to the database.
Use this when Celery workers are not available (e.g., no Redis connection).

Usage:
    # Scrape last 10 days for all companies
    python scripts/direct_scrape.py --days 10
    
    # Scrape specific company
    python scripts/direct_scrape.py --ticker AAPL --days 30
    
    # Scrape with verbose logging
    python scripts/direct_scrape.py --days 7 --verbose
    
    # Limit to first N companies (for testing)
    python scripts/direct_scrape.py --days 7 --limit 5
"""

import asyncio
import argparse
import platform
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List

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


async def process_single_filing(
    sec_client,
    db,
    filing_meta: Dict[str, Any],
    company_id: int,
    company_name: str,
    cik: str,
    ticker: str,
) -> int:
    """
    Process a single Form 4 filing: fetch XML, parse, and save trades.
    
    Returns:
        Number of trades created
    """
    from app.models.processed_filing import ProcessedFiling
    from app.models.company import Company
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert
    
    # Import parsing and saving functions from sec_tasks
    from app.tasks.sec_tasks import parse_form4_xml, save_trades_and_insiders
    
    accession_number = filing_meta.get("accession_number")
    filing_url = filing_meta.get("filing_url")
    filing_date_str = filing_meta.get("filing_date")
    
    if not accession_number or not filing_url:
        logger.warning(f"Missing accession_number or filing_url for {company_name}. Skipping.")
        return 0
    
    # Check if already processed
    existing = await db.execute(
        select(ProcessedFiling).filter(ProcessedFiling.accession_number == accession_number)
    )
    if existing.scalar_one_or_none():
        logger.debug(f"Filing {accession_number} already processed. Skipping.")
        return 0
    
    try:
        # Fetch the XML document
        xml_content = await sec_client.fetch_form4_document(filing_url)
    except ValueError as e:
        if "No raw XML document found" in str(e):
            logger.warning(f"No XML found for {accession_number}. Marking as processed.")
            # Mark as processed to avoid retrying
            filing_date = datetime.utcnow().date()
            if filing_date_str:
                try:
                    filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date()
                except (ValueError, AttributeError):
                    pass
            
            now_naive = datetime.utcnow().replace(tzinfo=None)
            processed_filing = ProcessedFiling(
                accession_number=accession_number,
                filing_url=filing_url,
                filing_date=filing_date,
                ticker=ticker,
                trades_created=0,
                processed_at=now_naive,
                created_at=now_naive,
            )
            db.add(processed_filing)
            return 0
        raise
    
    # Parse the XML
    parsed_data = parse_form4_xml(xml_content, cik, company_name)
    
    if parsed_data is None:
        logger.warning(f"No parsed data for {accession_number}. Skipping trades.")
        # Still mark as processed
        filing_date = datetime.utcnow().date()
        if filing_date_str:
            try:
                filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date()
            except (ValueError, AttributeError):
                pass
        
        now_naive = datetime.utcnow().replace(tzinfo=None)
        processed_filing = ProcessedFiling(
            accession_number=accession_number,
            filing_url=filing_url,
            filing_date=filing_date,
            ticker=ticker,
            trades_created=0,
            processed_at=now_naive,
            created_at=now_naive,
        )
        db.add(processed_filing)
        return 0
    
    # Prepare filing date
    filing_date = datetime.utcnow().date()
    if filing_date_str:
        try:
            filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date()
        except (ValueError, AttributeError):
            pass
    
    # Create ProcessedFiling entry (with ON CONFLICT DO NOTHING for race conditions)
    now_naive = datetime.utcnow().replace(tzinfo=None)
    stmt = insert(ProcessedFiling).values(
        accession_number=accession_number,
        filing_url=filing_url,
        filing_date=filing_date,
        ticker=ticker,
        trades_created=0,
        processed_at=now_naive,
        created_at=now_naive,
    ).on_conflict_do_nothing(index_elements=['accession_number'])
    
    result = await db.execute(stmt)
    
    if result.rowcount == 0:
        logger.debug(f"Filing {accession_number} already processed by another process.")
        return 0
    
    # Fetch the processed filing record
    processed_filing_result = await db.execute(
        select(ProcessedFiling).filter(ProcessedFiling.accession_number == accession_number)
    )
    processed_filing = processed_filing_result.scalar_one()
    
    # Save trades and insiders
    trades_count = await save_trades_and_insiders(
        db, processed_filing.id, parsed_data, company_id, filing_date, filing_url
    )
    
    # Update trades count
    processed_filing.trades_created = trades_count
    
    return trades_count


async def scrape_company_direct(
    sec_client,
    db,
    company_id: int,
    ticker: str,
    cik: str,
    company_name: str,
    days_back: int,
    max_filings: int = 100,
) -> Dict[str, Any]:
    """
    Directly scrape Form 4 filings for a single company.
    
    Returns:
        Dict with filings_found, new_filings, trades_created
    """
    from app.config import settings
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    try:
        # Fetch filings metadata from SEC
        filings_metadata = await sec_client.fetch_recent_form4_filings(
            cik=cik,
            count=max_filings,
            start_date=start_date
        )
    except Exception as e:
        logger.error(f"Error fetching filings for {ticker}: {e}")
        return {"filings_found": 0, "new_filings": 0, "trades_created": 0, "error": str(e)}
    
    if not filings_metadata:
        return {"filings_found": 0, "new_filings": 0, "trades_created": 0}
    
    total_trades = 0
    new_filings = 0
    
    for filing_meta in filings_metadata:
        try:
            trades = await process_single_filing(
                sec_client=sec_client,
                db=db,
                filing_meta=filing_meta,
                company_id=company_id,
                company_name=company_name,
                cik=cik,
                ticker=ticker,
            )
            if trades > 0:
                new_filings += 1
                total_trades += trades
        except Exception as e:
            logger.error(f"Error processing filing for {ticker}: {e}")
            continue
        
        # Rate limiting: respect SEC's 10 req/sec limit
        await asyncio.sleep(0.15)
    
    return {
        "filings_found": len(filings_metadata),
        "new_filings": new_filings,
        "trades_created": total_trades,
    }


async def direct_scrape(
    days_back: int = 30,
    ticker: Optional[str] = None,
    limit: Optional[int] = None,
    verbose: bool = False,
):
    """
    Main function to directly scrape SEC Form 4 filings.
    
    Args:
        days_back: Number of days to look back
        ticker: Optional specific ticker to scrape
        limit: Optional limit on number of companies to process
        verbose: Enable verbose logging
    """
    from app.database import db_manager
    from app.services.sec_client import SECClient
    from app.models import Company
    from app.config import settings
    from sqlalchemy import select
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 80)
    logger.info("DIRECT SEC SCRAPER - No Celery Required")
    logger.info("=" * 80)
    logger.info(f"Days back: {days_back}")
    if ticker:
        logger.info(f"Single company: {ticker}")
    if limit:
        logger.info(f"Limit: {limit} companies")
    logger.info("=" * 80)
    
    # Initialize SEC client
    sec_client = SECClient(user_agent=settings.sec_user_agent)
    
    # Get companies to scrape
    async with db_manager.get_session() as db:
        if ticker:
            result = await db.execute(
                select(Company).filter(
                    Company.ticker == ticker.upper(),
                    Company.cik.isnot(None)
                )
            )
            companies = result.scalars().all()
            if not companies:
                logger.error(f"Company {ticker} not found or has no CIK!")
                return
        else:
            result = await db.execute(select(Company).filter(Company.cik.isnot(None)))
            companies = result.scalars().all()
        
        if limit:
            companies = companies[:limit]
        
        logger.info(f"Found {len(companies)} companies to scrape")
        
        # Statistics
        total_filings = 0
        total_new_filings = 0
        total_trades = 0
        successful = 0
        failed = 0
        
        for i, company in enumerate(companies, 1):
            logger.info(f"[{i}/{len(companies)}] Scraping {company.ticker} ({company.name})...")
            
            try:
                result = await scrape_company_direct(
                    sec_client=sec_client,
                    db=db,
                    company_id=company.id,
                    ticker=company.ticker,
                    cik=company.cik,
                    company_name=company.name,
                    days_back=days_back,
                )
                
                total_filings += result.get("filings_found", 0)
                total_new_filings += result.get("new_filings", 0)
                total_trades += result.get("trades_created", 0)
                
                if result.get("error"):
                    failed += 1
                    logger.warning(f"  ✗ Error: {result['error'][:100]}")
                else:
                    successful += 1
                    if result.get("trades_created", 0) > 0:
                        logger.info(
                            f"  ✓ Found {result['filings_found']} filings, "
                            f"{result['new_filings']} new, "
                            f"{result['trades_created']} trades saved"
                        )
                    else:
                        logger.info(f"  ✓ {result['filings_found']} filings (all already processed)")
                
                # Commit after each company
                await db.commit()
                
            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Failed: {str(e)[:100]}")
                await db.rollback()
            
            # Rate limiting between companies
            await asyncio.sleep(0.2)
        
        logger.info("=" * 80)
        logger.info("SCRAPE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Companies processed: {successful + failed}")
        logger.info(f"Successful: {successful}, Failed: {failed}")
        logger.info(f"Total filings found: {total_filings}")
        logger.info(f"New filings processed: {total_new_filings}")
        logger.info(f"Total trades saved: {total_trades}")
        logger.info("=" * 80)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Direct SEC Scraper - Scrapes SEC Form 4 filings without Celery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape last 10 days for all companies
  python scripts/direct_scrape.py --days 10
  
  # Scrape specific company
  python scripts/direct_scrape.py --ticker AAPL --days 30
  
  # Test with first 5 companies
  python scripts/direct_scrape.py --days 7 --limit 5
  
  # Verbose logging
  python scripts/direct_scrape.py --days 7 --verbose
        """
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)"
    )
    
    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help="Specific ticker to scrape (optional)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit to first N companies (optional, for testing)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging"
    )
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    logger.info(f"Starting direct scrape at {start_time.isoformat()}")
    
    try:
        await direct_scrape(
            days_back=args.days,
            ticker=args.ticker,
            limit=args.limit,
            verbose=args.verbose,
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Completed in {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info("✓ Direct scrape finished successfully!")
        
    except KeyboardInterrupt:
        logger.warning("Scrape interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scrape failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

