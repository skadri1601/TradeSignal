from app.core.celery_app import celery_app
import logging
from app.config import settings
from app.core.redis_cache import get_cache
from app.services.sec_client import SECClient
from app.services.form4_parser import Form4Parser
from app.services.insider_service import InsiderService
from app.database import get_db, db_manager
from app.models.company import Company
from app.models.processed_filing import ProcessedFiling
from app.models.trade import Trade
from app.models.insider import Insider
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

# Initialize SECClient once for tasks, it handles its own rate limiting
sec_client = SECClient(user_agent=settings.sec_user_agent)

@celery_app.task(name="update_cik_for_company")
def update_cik_for_company_task(company_id: int, ticker: str):
    """
    Celery task to update CIK for a specific company by its ticker.
    This might be triggered when a new company is added or a ticker changes.
    """
    async def _async_task():
        logger.info(f"Attempting to update CIK for Company ID: {company_id}, Ticker: {ticker}")
        cik = await sec_client.lookup_cik_by_ticker(ticker)
        if cik:
            async with db_manager.get_session() as db:
                result = await db.execute(select(Company).filter(Company.id == company_id))
                company = result.scalar_one_or_none()
                if company:
                    company.cik = cik
                    company.updated_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"Updated CIK for company {ticker} ({company_id}) to {cik}")
                else:
                    logger.warning(f"Company with ID {company_id} not found to update CIK.")
        else:
            logger.warning(f"Could not find CIK for company {ticker} ({company_id}).")
    
    asyncio.run(_async_task())

@celery_app.task(name="scrape_recent_form4_filings")
def scrape_recent_form4_filings(company_info: Dict[str, Any]):
    """
    Celery task to scrape recent Form 4 filings for a given company.
    company_info dict must contain 'company_id', 'cik', 'ticker', 'name'.
    """
    async def _async_task():
        company_id = company_info['company_id']
        cik = company_info['cik']
        company_name = company_info['name']
        company_ticker = company_info['ticker']

        logger.info(f"Scraping recent Form 4 filings for CIK: {cik} ({company_name}, {company_ticker})")
        
        try:
            # Fetch filings metadata
            filings_metadata = await sec_client.fetch_recent_form4_filings(cik=cik, count=settings.scraper_max_filings)
            
            if not filings_metadata:
                logger.info(f"No new Form 4 filings found for {company_name} (CIK: {cik}).")
                return

            logger.info(f"Found {len(filings_metadata)} filings for {company_name} ({company_ticker}). Processing...")
            new_filings_count = 0
            skipped_filings_count = 0

            for filing_meta in filings_metadata:
                accession_number = filing_meta.get("accession_number")
                filing_url = filing_meta.get("filing_url")
                filing_date_str = filing_meta.get("filing_date")

                if not accession_number or not filing_url:
                    logger.warning(f"Missing accession_number or filing_url for a filing of {company_name}. Skipping.")
                    continue
                
                # Check if this filing has already been processed
                async with db_manager.get_session() as db:
                    existing_filing = await db.execute(
                        select(ProcessedFiling).filter(ProcessedFiling.accession_number == accession_number)
                    )
                    if existing_filing.scalar_one_or_none():
                        skipped_filings_count += 1
                        logger.debug(f"Filing {accession_number} for {company_name} already processed. Skipping.")
                        continue

                    logger.info(f"New filing {accession_number} found for {company_name}. Enqueuing for processing.")
                    # Enqueue task to process the document
                    process_form4_document_task.delay(
                        filing_url, 
                        company_id, 
                        cik, 
                        company_name, 
                        accession_number, 
                        filing_date_str
                    )
                    new_filings_count += 1

            logger.info(
                f"Completed scraping for {company_name} ({company_ticker}): "
                f"{new_filings_count} new filings enqueued, {skipped_filings_count} already processed"
            )

        except Exception as e:
            logger.error(f"Error scraping Form 4 filings for {company_name} (CIK: {cik}): {e}", exc_info=True)
    
    asyncio.run(_async_task())


@celery_app.task(name="scrape_all_active_companies_form4_filings")
def scrape_all_active_companies_form4_filings_task():
    """
    Orchestrator task to scrape Form 4 filings for all active companies in the database.
    
    Implements cooldown mechanism to skip recently scraped companies and processing
    limits to prevent queue overflow.
    """
    async def _async_task():
        logger.info("Starting scrape_all_active_companies_form4_filings_task...")
        
        cooldown_hours = settings.scraper_cooldown_hours
        max_companies = settings.scraper_max_companies_per_run
        cooldown_cutoff = datetime.utcnow() - timedelta(hours=cooldown_hours)
        
        async with db_manager.get_session() as db:
            # Get all companies with CIK
            companies_result = await db.execute(select(Company).filter(Company.cik.isnot(None)))
            all_companies = companies_result.scalars().all()
            total_companies = len(all_companies)
            
            logger.info(f"Found {total_companies} companies with CIK. Checking cooldown (last {cooldown_hours} hours)...")
            
            # Get last scrape time per company (by ticker)
            # Query ProcessedFiling to find the most recent processed_at for each ticker
            last_scrape_query = (
                select(
                    ProcessedFiling.ticker,
                    func.max(ProcessedFiling.processed_at).label("last_scraped_at")
                )
                .where(ProcessedFiling.ticker.isnot(None))
                .group_by(ProcessedFiling.ticker)
            )
            last_scrape_result = await db.execute(last_scrape_query)
            last_scrapes = {row.ticker: row.last_scraped_at for row in last_scrape_result.all()}
            
            # Filter companies: skip those within cooldown, prioritize others
            companies_to_process = []
            skipped_count = 0
            
            for company in all_companies:
                last_scraped = last_scrapes.get(company.ticker)
                
                if last_scraped:
                    # Convert timezone-aware datetime to naive for comparison
                    if last_scraped.tzinfo is not None:
                        last_scraped = last_scraped.replace(tzinfo=None)
                    
                    if last_scraped > cooldown_cutoff:
                        skipped_count += 1
                        logger.debug(
                            f"Skipping {company.name} ({company.ticker}): "
                            f"last scraped {last_scraped.strftime('%Y-%m-%d %H:%M:%S')} "
                            f"(within {cooldown_hours}h cooldown)"
                        )
                        continue
                
                companies_to_process.append(company)
            
            # Apply processing limit
            companies_enqueued = 0
            if len(companies_to_process) > max_companies:
                logger.info(
                    f"Processing limit reached: {len(companies_to_process)} companies eligible, "
                    f"limiting to {max_companies} companies per run"
                )
                companies_to_process = companies_to_process[:max_companies]
            
            # Enqueue scraping tasks
            for company in companies_to_process:
                logger.info(f"Enqueuing scrape for company: {company.name} ({company.ticker}, CIK: {company.cik})")
                company_info = {
                    "company_id": company.id,
                    "cik": company.cik,
                    "ticker": company.ticker,
                    "name": company.name
                }
                scrape_recent_form4_filings.delay(company_info)
                companies_enqueued += 1
            
            logger.info(
                f"Finished enqueuing Form 4 scraping tasks: "
                f"{companies_enqueued} enqueued, {skipped_count} skipped (cooldown), "
                f"{total_companies} total companies"
            )
    
    asyncio.run(_async_task())


@celery_app.task(name="process_form4_document")
def process_form4_document_task(
    filing_url: str,
    company_id: int,
    cik: str,
    company_name: str,
    accession_number: str,
    filing_date_str: str,
):
    """
    Celery task to fetch and process a single Form 4 XML document.
    """
    async def _async_task():
        logger.info(f"Processing Form 4 document for {accession_number} ({company_name})...")
        try:
            try:
                xml_content = await sec_client.fetch_form4_document(filing_url)
            except ValueError as e:
                # Handle missing XML document gracefully
                if "No raw XML document found" in str(e):
                    logger.warning(
                        f"No raw XML document found for filing {accession_number} ({company_name}). "
                        f"Filing URL: {filing_url}. This may be a filing format issue. Skipping."
                    )
                    # Mark as processed to avoid retrying indefinitely
                    async with db_manager.get_session() as db:
                        company_result = await db.execute(
                            select(Company).where(Company.id == company_id)
                        )
                        company = company_result.scalar_one_or_none()
                        ticker = company.ticker if company else None
                        
                        filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date()
                        now_naive = datetime.utcnow().replace(tzinfo=None)
                        processed_filing = ProcessedFiling(
                            accession_number=accession_number,
                            filing_url=filing_url,
                            filing_date=filing_date,
                            ticker=ticker,
                            trades_created=0,  # No trades created due to missing XML
                            processed_at=now_naive,
                            created_at=now_naive,
                        )
                        db.add(processed_filing)
                        await db.commit()
                        logger.info(f"Marked filing {accession_number} as processed (no XML found)")
                    return
                else:
                    # Re-raise other ValueError exceptions
                    raise
            
            parsed_data = parse_form4_xml(xml_content, cik, company_name)

            # Skip if parsing failed (no reportingOwner found)
            if parsed_data is None:
                logger.warning(f"No parsed data for {accession_number} - skipping trade saving")
                async with db_manager.get_session() as db:
                    # Still create ProcessedFiling entry to track that we attempted processing
                    company_result = await db.execute(
                        select(Company).where(Company.id == company_id)
                    )
                    company = company_result.scalar_one_or_none()
                    ticker = company.ticker if company else None
                    
                    filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date()
                    now_naive = datetime.utcnow().replace(tzinfo=None)
                    processed_filing = ProcessedFiling(
                        accession_number=accession_number,
                        filing_url=filing_url,
                        filing_date=filing_date,
                        ticker=ticker,
                        trades_created=0,  # No trades created
                        processed_at=now_naive,
                        created_at=now_naive,
                    )
                    db.add(processed_filing)
                    await db.commit()
                    logger.info(f"Processed filing {accession_number} saved (no trades - no reportingOwner found)")
                return

            async with db_manager.get_session() as db:
                # Get company to retrieve ticker
                company_result = await db.execute(
                    select(Company).where(Company.id == company_id)
                )
                company = company_result.scalar_one_or_none()
                ticker = company.ticker if company else None
                
                # Create ProcessedFiling entry (only with fields that exist in the model)
                filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date() # Ensure date only
                # Use timezone-naive datetime for TIMESTAMP WITHOUT TIME ZONE columns
                now_naive = datetime.utcnow().replace(tzinfo=None)
                processed_filing = ProcessedFiling(
                    accession_number=accession_number,
                    filing_url=filing_url,
                    filing_date=filing_date,
                    ticker=ticker,
                    trades_created=0,  # Will be updated after trades are saved
                    processed_at=now_naive,
                    created_at=now_naive,
                )
                db.add(processed_filing)
                await db.flush() # Flush to get processed_filing.id

                # Save trades and insiders (pass company_id, filing_date, filing_url we already have)
                trades_count = await save_trades_and_insiders(db, processed_filing.id, parsed_data, company_id, filing_date, filing_url)
                
                # Update trades_created count
                processed_filing.trades_created = trades_count
                
                await db.commit()
                logger.info(f"Successfully processed and saved Form 4 filing {accession_number} for {company_name}.")

        except Exception as e:
            logger.error(f"Error processing Form 4 document {accession_number} for {company_name}: {e}", exc_info=True)
            # Note: ProcessedFiling doesn't track parsing status, so we just log the error
    
    asyncio.run(_async_task())


def parse_form4_xml(xml_content: str, cik: str, company_name: str) -> Dict[str, Any]:
    """
    Parse Form 4 XML content and extract relevant trade and insider data.
    Uses the Form4Parser class for robust parsing.
    """
    try:
        # Use the Form4Parser class for better XML handling
        parsed = Form4Parser.parse(xml_content)
        
        # Check if we have a reporting owner
        reporting_owner = parsed.get("reporting_owner", {})
        if not reporting_owner or not reporting_owner.get("cik"):
            logger.warning(f"No reportingOwner found in Form 4 XML for CIK {cik}. Skipping this filing.")
            return None
        
        # Extract issuer info
        issuer = parsed.get("issuer", {})
        
        # Convert transactions to the expected format
        all_trades_data = []
        for txn in parsed.get("transactions", []):
            # Convert transaction date format if needed
            transaction_date = txn.get("transaction_date", "")
            if hasattr(transaction_date, 'strftime'):  # date object
                transaction_date = transaction_date.strftime("%Y-%m-%d")
            elif isinstance(transaction_date, str) and "T" in transaction_date:
                transaction_date = transaction_date.split("T")[0]
            elif not transaction_date:
                continue  # Skip transactions without dates
            
            # Determine acquired/disposed code
            txn_type = txn.get("transaction_type", "")
            acquired_disposed_code = "A" if txn_type == "BUY" else "D"
            
            trade_data = {
                "security_title": txn.get("security_title", ""),
                "transaction_date": transaction_date,
                "transaction_shares": float(txn.get("shares", 0)),
                "transaction_price_per_share": float(txn.get("price_per_share", 0)) if txn.get("price_per_share") else 0.0,
                "transaction_code": txn.get("transaction_code", ""),
                "equity_swap_involved": "",  # Not in Form4Parser output
                "acquired_disposed_code": acquired_disposed_code,
                "shares_owned_after_transaction": float(txn.get("shares_owned_after", 0)),
                "direct_indirect_ownership": txn.get("ownership_type", "Direct"),  # "Direct" or "Indirect"
                "nature_of_ownership": "",  # Not in Form4Parser output
                "is_derivative": txn.get("derivative_transaction", False),
            }
            
            # Add derivative-specific fields if applicable
            if trade_data["is_derivative"]:
                trade_data["conversion_exercise_price"] = 0.0  # Not extracted by Form4Parser
                trade_data["underlying_security_title"] = ""  # Not extracted by Form4Parser
                trade_data["underlying_security_shares"] = ""  # Not extracted by Form4Parser
            
            all_trades_data.append(trade_data)
        
        # Return in the expected format
        # Note: Form4Parser doesn't extract address, so we'll use empty strings
        return {
            "owner_name": reporting_owner.get("name", ""),
            "owner_cik": reporting_owner.get("cik", ""),
            "owner_address": {
                "street1": "",
                "street2": "",
                "city": "",
                "state": "",
                "zip": "",
                "state_description": "",
            },
            "issuer_cik": issuer.get("cik", ""),
            "issuer_name": issuer.get("name", ""),
            "issuer_ticker": issuer.get("ticker", ""),
            "trades": all_trades_data
        }
    except Exception as e:
        logger.error(f"Error parsing Form 4 XML for CIK {cik}: {e}", exc_info=True)
        return None


async def save_trades_and_insiders(db: AsyncSession, processed_filing_id: int, parsed_data: Dict[str, Any], company_id: int, filing_date: date, filing_url: str) -> int:
    """
    Save parsed trade and insider data to the database.

    Args:
        db: Database session
        processed_filing_id: ID of the ProcessedFiling record
        parsed_data: Parsed Form 4 data
        company_id: Company ID (already known from task context)
        filing_date: Date of the SEC filing
        filing_url: URL to the SEC filing

    Returns:
        Number of trades created
    """
    trades_created = 0
    
    # Get the company (we already have company_id from task context)
    company_result = await db.execute(select(Company).where(Company.id == company_id))
    company = company_result.scalar_one_or_none()
    
    if not company:
        logger.error(f"Company with ID {company_id} not found in database")
        return 0
    
    # Find or create Insider using name and company_id (not CIK)
    owner_name = parsed_data["owner_name"]
    # Extract title from parsed data if available (Form4Parser doesn't extract this, but we can try)
    owner_title = None  # Could be extracted from relationship data if needed
    
    # Use InsiderService.get_or_create which handles name + company_id lookup
    insider = await InsiderService.get_or_create(
        db=db,
        name=owner_name,
        company_id=company.id,
        title=owner_title,
        # Note: Form4Parser doesn't extract is_director/is_officer flags, 
        # but we could add that if the parser is enhanced
    )
    
    logger.info(f"Found/created insider: {insider.name} (Company: {company.ticker})")


    # Save Trades
    for trade_data in parsed_data["trades"]:
        try:
            transaction_date = datetime.strptime(trade_data["transaction_date"], "%Y-%m-%d").date()
            trade_type = "BUY" if trade_data["acquired_disposed_code"] == "A" else "SELL"

            # Calculate total value
            shares = trade_data["transaction_shares"]
            price = trade_data["transaction_price_per_share"]
            total_value = shares * price if shares and price else None

            # Check if this exact trade already exists (to prevent duplicates if re-processing)
            existing_trade_result = await db.execute(
                select(Trade).filter(
                    Trade.insider_id == insider.id,
                    Trade.company_id == company.id,
                    Trade.transaction_date == transaction_date,
                    Trade.shares == shares,
                    Trade.price_per_share == price,
                    Trade.transaction_type == trade_type
                ).limit(1)
            )
            existing_trade = existing_trade_result.first()
            if existing_trade:
                logger.debug(f"Duplicate trade found for insider {insider.id}, company {company.id}. Skipping.")
                continue

            # Map to actual Trade model columns
            trade = Trade(
                insider_id=insider.id,
                company_id=company.id,
                transaction_date=transaction_date,
                filing_date=filing_date,  # Use filing date from processed_filing
                transaction_type=trade_type,
                transaction_code=trade_data["transaction_code"],
                shares=shares,
                price_per_share=price,
                total_value=total_value,
                shares_owned_after=trade_data["shares_owned_after_transaction"],
                ownership_type=trade_data["direct_indirect_ownership"],
                derivative_transaction=trade_data["is_derivative"],
                sec_filing_url=filing_url,
                form_type="Form 4",
                notes=trade_data.get("security_title", "")  # Store security title in notes
            )
            db.add(trade)
            trades_created += 1
            logger.debug(f"Added trade for {insider.name} in {company.ticker}: {trade_type} {shares} shares at ${price}")
        except Exception as e:
            logger.error(f"Error saving trade for filing {processed_filing_id}: {e}, trade data: {trade_data}", exc_info=True)

    return trades_created
