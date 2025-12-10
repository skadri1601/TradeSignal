from app.core.celery_app import celery_app
import logging
from app.config import settings
from app.core.redis_cache import get_cache
from app.services.sec_client import SECClient
from app.database import get_db, db_manager
from app.models.company import Company
from app.models.processed_filing import ProcessedFiling
from app.models.trade import Trade
from app.models.insider import Insider
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
import asyncio

logger = logging.getLogger(__name__)

# Initialize SECClient once for tasks, it handles its own rate limiting
sec_client = SECClient(user_agent=settings.sec_user_agent)

@celery_app.task(name="update_cik_for_company")
async def update_cik_for_company_task(company_id: int, ticker: str):
    """
    Celery task to update CIK for a specific company by its ticker.
    This might be triggered when a new company is added or a ticker changes.
    """
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

@celery_app.task(name="scrape_recent_form4_filings")
async def scrape_recent_form4_filings(company_info: Dict[str, Any]):
    """
    Celery task to scrape recent Form 4 filings for a given company.
    company_info dict must contain 'company_id', 'cik', 'ticker', 'name'.
    """
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


@celery_app.task(name="scrape_all_active_companies_form4_filings")
async def scrape_all_active_companies_form4_filings_task():
    """
    Orchestrator task to scrape Form 4 filings for all active companies in the database.
    """
    logger.info("Starting scrape_all_active_companies_form4_filings_task...")
    async with db_manager.get_session() as db:
        companies_result = await db.execute(select(Company).filter(Company.cik.isnot(None), Company.is_active == True))
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


@celery_app.task(name="process_form4_document")
async def process_form4_document_task(
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
    logger.info(f"Processing Form 4 document for {accession_number} ({company_name})...")
    try:
        xml_content = await sec_client.fetch_form4_document(filing_url)
        parsed_data = parse_form4_xml(xml_content, cik, company_name)

        async with db_manager.get_session() as db:
            # Create ProcessedFiling entry
            filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date() # Ensure date only
            processed_filing = ProcessedFiling(
                company_id=company_id,
                accession_number=accession_number,
                filing_url=filing_url,
                filing_date=filing_date,
                form_type="4", # Hardcoded for now
                document_content=xml_content,
                is_parsed=True,
                parsed_at=datetime.utcnow()
            )
            db.add(processed_filing)
            await db.flush() # Flush to get processed_filing.id

            # Save trades and insiders
            await save_trades_and_insiders(db, processed_filing.id, parsed_data)
            await db.commit()
            logger.info(f"Successfully processed and saved Form 4 filing {accession_number} for {company_name}.")

    except Exception as e:
        logger.error(f"Error processing Form 4 document {accession_number} for {company_name}: {e}", exc_info=True)
        # Mark filing as unparsed if an error occurs during processing
        async with db_manager.get_session() as db:
            existing_filing = await db.execute(
                select(ProcessedFiling).filter(ProcessedFiling.accession_number == accession_number)
            )
            filing = existing_filing.scalar_one_or_none()
            if filing:
                filing.is_parsed = False
                await db.commit()


def parse_form4_xml(xml_content: str, cik: str, company_name: str) -> Dict[str, Any]:
    """
    Parse Form 4 XML content and extract relevant trade and insider data.
    """
    root = ET.fromstring(xml_content)
    
    # Define namespaces
    ns = {
        'n1': 'http://www.sec.gov/edgar/document/thirteen/rules/10b5-1',
        'n2': 'http://www.sec.gov/edgar/document/thirteen/rules/rule144',
        'n3': 'http://www.sec.gov/edgar/thirteen/form4' # Main namespace for Form 4
    }

    # Helper to find text in an element
    def find_text(element, xpath, default=''):
        found = element.find(xpath, ns)
        return found.text.strip() if found is not None and found.text is not None else default

    # Extract reporting owner (insider) info
    reporting_owner = root.find('n3:reportingOwner', ns)
    owner_name = find_text(reporting_owner, 'n3:reportingOwnerId/n3:rptOwnerName')
    owner_cik = find_text(reporting_owner, 'n3:reportingOwnerId/n3:rptOwnerCik')
    owner_street1 = find_text(reporting_owner, 'n3:reportingOwnerAddress/n3:rptOwnerStreet1')
    owner_street2 = find_text(reporting_owner, 'n3:reportingOwnerAddress/n3:rptOwnerStreet2')
    owner_city = find_text(reporting_owner, 'n3:reportingOwnerAddress/n3:rptOwnerCity')
    owner_state = find_text(reporting_owner, 'n3:reportingOwnerAddress/n3:rptOwnerState')
    owner_zip = find_text(reporting_owner, 'n3:reportingOwnerAddress/n3:rptOwnerZipCode')
    owner_state_description = find_text(reporting_owner, 'n3:reportingOwnerAddress/n3:rptOwnerStateDescription')

    # Extract issuer (company) info
    issuer = root.find('n3:issuer', ns)
    issuer_cik = find_text(issuer, 'n3:issuerCik')
    issuer_name = find_text(issuer, 'n3:issuerName')
    issuer_ticker = find_text(issuer, 'n3:issuerTradingSymbol')

    # Extract transaction data
    all_trades_data = []

    def extract_trade_details(transaction_node):
        security_title = find_text(transaction_node, 'n3:securityTitle/n3:value')
        transaction_date_str = find_text(transaction_node, 'n3:transactionDate/n3:value')
        
        # Transaction amount/shares
        transaction_shares = find_text(transaction_node, 'n3:transactionAmounts/n3:transactionShares/n3:value')
        transaction_price = find_text(transaction_node, 'n3:transactionAmounts/n3:transactionPricePerShare/n3:value')
        transaction_acq_dis = find_text(transaction_node, 'n3:transactionAmounts/n3:transactionAcquiredDisposedCode/n3:value') # A for acquired, D for disposed
        
        # Ownership data after transaction
        shares_owned_after = find_text(transaction_node, 'n3:postTransactionAmounts/n3:sharesOwnedFollowingTransaction/n3:value')
        
        # Conversion to float/int, handle potential errors
        try:
            shares = float(transaction_shares) if transaction_shares else 0.0
            price = float(transaction_price) if transaction_price else 0.0
            shares_after = float(shares_owned_after) if shares_owned_after else 0.0
        except ValueError:
            shares = 0.0
            price = 0.0
            shares_after = 0.0
            logger.warning(f"Could not convert shares/price to float for {owner_name}, CIK {cik}")

        return {
            "security_title": security_title,
            "transaction_date": transaction_date_str,
            "transaction_shares": shares,
            "transaction_price_per_share": price,
            "transaction_code": find_text(transaction_node, 'n3:transactionCoding/n3:transactionCode'),
            "equity_swap_involved": find_text(transaction_node, 'n3:transactionCoding/n3:equitySwapInvolved'),
            "acquired_disposed_code": transaction_acq_dis,
            "shares_owned_after_transaction": shares_after,
            "direct_indirect_ownership": find_text(transaction_node, 'n3:ownershipNature/n3:directOrIndirectOwnership/n3:value'),
            "nature_of_ownership": find_text(transaction_node, 'n3:ownershipNature/n3:natureOfOwnership/n3:value'),
        }

    # Non-derivative transactions (Table I)
    for non_deriv_table in root.findall('n3:nonDerivativeTable/n3:nonDerivativeTransaction', ns):
        trade = extract_trade_details(non_deriv_table)
        trade["is_derivative"] = False
        all_trades_data.append(trade)

    # Derivative transactions (Table II)
    for deriv_table in root.findall('n3:derivativeTable/n3:derivativeTransaction', ns):
        trade = extract_trade_details(deriv_table)
        trade["is_derivative"] = True
        # Additional derivative-specific fields
        conversion_exercise_price = find_text(deriv_table, 'n3:conversionOrExercisePrice/n3:value')
        trade["conversion_exercise_price"] = float(conversion_exercise_price) if conversion_exercise_price else 0.0
        trade["underlying_security_title"] = find_text(deriv_table, 'n3:underlyingSecurity/n3:underlyingSecurityTitle')
        trade["underlying_security_shares"] = find_text(deriv_table, 'n3:underlyingSecurity/n3:underlyingSecurityShares')
        all_trades_data.append(trade)

    return {
        "owner_name": owner_name,
        "owner_cik": owner_cik,
        "owner_address": {
            "street1": owner_street1,
            "street2": owner_street2,
            "city": owner_city,
            "state": owner_state,
            "zip": owner_zip,
            "state_description": owner_state_description,
        },
        "issuer_cik": issuer_cik,
        "issuer_name": issuer_name,
        "issuer_ticker": issuer_ticker,
        "trades": all_trades_data
    }


async def save_trades_and_insiders(db: AsyncSession, processed_filing_id: int, parsed_data: Dict[str, Any]):
    """
    Save parsed trade and insider data to the database.
    """
    # Find or create Insider
    insider_cik = parsed_data["owner_cik"]
    result = await db.execute(select(Insider).filter(Insider.cik == insider_cik))
    insider = result.scalar_one_or_none()

    if not insider:
        insider = Insider(
            cik=insider_cik,
            name=parsed_data["owner_name"],
            address_street1=parsed_data["owner_address"]["street1"],
            address_street2=parsed_data["owner_address"]["street2"],
            address_city=parsed_data["owner_address"]["city"],
            address_state=parsed_data["owner_address"]["state"],
            address_zip=parsed_data["owner_address"]["zip"],
            address_state_description=parsed_data["owner_address"]["state_description"],
            # Add any other relevant insider fields
        )
        db.add(insider)
        await db.flush() # Flush to get insider.id
        logger.info(f"Created new insider: {insider.name} (CIK: {insider.cik})")
    else:
        logger.debug(f"Insider already exists: {insider.name} (CIK: {insider.cik})")
        # Update existing insider info if necessary
        insider.name = parsed_data["owner_name"]
        insider.address_street1=parsed_data["owner_address"]["street1"]
        insider.address_street2=parsed_data["owner_address"]["street2"]
        insider.address_city=parsed_data["owner_address"]["city"]
        insider.address_state=parsed_data["owner_address"]["state"]
        insider.address_zip=parsed_data["owner_address"]["zip"]
        insider.address_state_description=parsed_data["owner_address"]["state_description"]
        insider.updated_at = datetime.utcnow()

    # Find or create Company (if not already existing from the main scraper)
    issuer_cik = parsed_data["issuer_cik"]
    result = await db.execute(select(Company).filter(Company.cik == issuer_cik))
    company = result.scalar_one_or_none()

    if not company:
        # This case should ideally not happen if companies are pre-populated,
        # but handle it for robustness
        company = Company(
            cik=issuer_cik,
            name=parsed_data["issuer_name"],
            ticker=parsed_data["issuer_ticker"],
            # Other fields will be enriched later
        )
        db.add(company)
        await db.flush()
        logger.info(f"Created new company from Form 4: {company.name} (CIK: {company.cik})")
    else:
        logger.debug(f"Company already exists: {company.name} (CIK: {company.cik})")
        # Update ticker if changed (unlikely for CIK)
        company.ticker = parsed_data["issuer_ticker"]
        company.updated_at = datetime.utcnow()

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
            logger.debug(f"Added trade for {insider.name} in {company.ticker}: {trade_type} {trade.transaction_shares} shares of {trade.security_title} at ${trade.transaction_price_per_share}")
        except Exception as e:
            logger.error(f"Error saving trade for filing {processed_filing_id}: {e}, trade data: {trade_data}", exc_info=True)
