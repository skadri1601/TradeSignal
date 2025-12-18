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
from sqlalchemy import select, and_
from datetime import datetime, timedelta
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

        except Exception as e:
            logger.error(f"Error scraping Form 4 filings for {company_name} (CIK: {cik}): {e}", exc_info=True)
    
    asyncio.run(_async_task())


@celery_app.task(name="scrape_all_active_companies_form4_filings")
def scrape_all_active_companies_form4_filings_task():
    """
    Orchestrator task to scrape Form 4 filings for all active companies in the database.
    """
    async def _async_task():
        logger.info("Starting scrape_all_active_companies_form4_filings_task...")
        async with db_manager.get_session() as db:
            companies_result = await db.execute(select(Company).filter(Company.cik.isnot(None)))
            companies = companies_result.scalars().all()
            
            for company in companies:
                logger.info(f"Enqueuing scrape for company: {company.name} (CIK: {company.cik})")
                company_info = {
                    "company_id": company.id,
                    "cik": company.cik,
                    "ticker": company.ticker,
                    "name": company.name
                }
                scrape_recent_form4_filings.delay(company_info) # Call the task by name (string)
        logger.info("Finished enqueuing Form 4 scraping tasks for all active companies.")
    
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
            xml_content = await sec_client.fetch_form4_document(filing_url)
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

                # Save trades and insiders (pass company_id we already have)
                trades_count = await save_trades_and_insiders(db, processed_filing.id, parsed_data, company_id)
                
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


async def save_trades_and_insiders(db: AsyncSession, processed_filing_id: int, parsed_data: Dict[str, Any], company_id: int) -> int:
    """
    Save parsed trade and insider data to the database.
    
    Args:
        db: Database session
        processed_filing_id: ID of the ProcessedFiling record
        parsed_data: Parsed Form 4 data
        company_id: Company ID (already known from task context)
    
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
            
            # Check if this exact trade already exists (to prevent duplicates if re-processing)
            # This is a simple check; more robust would involve hashing trade details
            existing_trade = await db.execute(
                select(Trade).filter(
                    Trade.processed_filing_id == processed_filing_id,
                    Trade.insider_id == insider.id,
                    Trade.company_id == company.id,
                    Trade.transaction_date == transaction_date,
                    Trade.transaction_shares == trade_data["transaction_shares"],
                    Trade.transaction_price_per_share == trade_data["transaction_price_per_share"],
                    Trade.transaction_type == trade_type,
                    Trade.security_title == trade_data["security_title"]
                )
            )
            if existing_trade.scalar_one_or_none():
                logger.debug(f"Duplicate trade found for filing {processed_filing_id}, insider {insider.id}, company {company.id}. Skipping.")
                continue


            trade = Trade(
                processed_filing_id=processed_filing_id,
                insider_id=insider.id,
                company_id=company.id,
                security_title=trade_data["security_title"],
                transaction_date=transaction_date,
                transaction_shares=trade_data["transaction_shares"],
                price_per_share=trade_data["transaction_price_per_share"],
                transaction_code=trade_data["transaction_code"],
                equity_swap_involved=trade_data["equity_swap_involved"].lower() == 'true',
                acquired_disposed_code=trade_data["acquired_disposed_code"],
                shares_owned_after_transaction=trade_data["shares_owned_after_transaction"],
                direct_indirect_ownership=trade_data["direct_indirect_ownership"],
                nature_of_ownership=trade_data["nature_of_ownership"],
                is_derivative=trade_data["is_derivative"],
                conversion_exercise_price=trade_data.get("conversion_exercise_price"),
                underlying_security_title=trade_data.get("underlying_security_title"),
                underlying_security_shares=trade_data.get("underlying_security_shares"),
                transaction_type=trade_type
            )
            db.add(trade)
            trades_created += 1
            logger.debug(f"Added trade for {insider.name} in {company.ticker}: {trade_type} {trade.transaction_shares} shares of {trade.security_title} at ${trade.transaction_price_per_share}")
        except Exception as e:
            logger.error(f"Error saving trade for filing {processed_filing_id}: {e}, trade data: {trade_data}", exc_info=True)
    
    return trades_created
