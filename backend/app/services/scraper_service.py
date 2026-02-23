"""
SEC Form 4 Scraper Service - Direct Mode (No Celery)

Orchestrates fetching Form 4 filings from SEC and saving to database.
Resource-optimized for $7 Render tier (512MB RAM, shared CPU).
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.insider import Insider
from app.models.trade import Trade

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Direct SEC Form 4 scraper (no Celery).
    Resource-optimized for $7 Render tier.
    """

    DEFAULT_MAX_FILINGS = 50
    DEFAULT_DAYS_BACK = 60

    def __init__(self):
        """Initialize scraper service with lazy-loaded clients."""
        self._sec_client = None

    def _get_sec_client(self):
        """Lazy-load SEC client to save memory."""
        if self._sec_client is None:
            from app.services.sec_client import SECClient
            self._sec_client = SECClient()
        return self._sec_client

    async def scrape_company_trades(
        self,
        db: AsyncSession,
        ticker: Optional[str] = None,
        cik: Optional[str] = None,
        days_back: int = 60,
        max_filings: int = 50,
    ) -> Dict[str, Any]:
        """
        Scrape Form 4 filings for a company directly (no Celery).

        Resource-optimized: processes one company at a time with limits.

        Args:
            db: Database session
            ticker: Company ticker symbol
            cik: Company CIK
            days_back: Days to look back for filings (default: 30)
            max_filings: Max filings to process per company (default: 5)

        Returns:
            Dict with success status, filings_processed, trades_created
        """
        if not ticker and not cik:
            raise ValueError("Must provide either ticker or CIK")

        # Apply resource limits
        max_filings = min(max_filings, self.DEFAULT_MAX_FILINGS)
        days_back = min(days_back, self.DEFAULT_DAYS_BACK)

        # Find company in DB
        company = None
        if ticker:
            result = await db.execute(
                select(Company).where(Company.ticker == ticker.upper())
            )
            company = result.scalar_one_or_none()
        elif cik:
            result = await db.execute(
                select(Company).where(Company.cik == cik)
            )
            company = result.scalar_one_or_none()

        if not company:
            logger.warning(f"Company {ticker or cik} not found in DB")
            return {"success": False, "message": "Company not found in database"}

        if not company.cik:
            # Try to look up CIK from SEC
            sec_client = self._get_sec_client()
            looked_up_cik = await sec_client.lookup_cik_by_ticker(company.ticker)
            if looked_up_cik:
                company.cik = looked_up_cik
                await db.flush()
                logger.info(f"Updated CIK for {company.ticker}: {looked_up_cik}")
            else:
                logger.warning(f"No CIK found for {ticker}")
                return {"success": False, "message": "CIK not found for company"}

        try:
            sec_client = self._get_sec_client()

            # Fetch recent filings (limited)
            start_date = datetime.now() - timedelta(days=days_back)
            filings = await sec_client.fetch_recent_form4_filings(
                cik=company.cik,
                start_date=start_date,
                count=max_filings
            )

            if not filings:
                logger.info(f"No Form 4 filings found for {company.ticker}")
                return {"success": True, "filings_processed": 0, "trades_created": 0}

            trades_created = 0
            filings_processed = 0

            for filing in filings:
                try:
                    # Skip if we already processed this filing
                    if await self._filing_already_processed(db, filing, company.id):
                        logger.debug(f"Skipping already processed filing: {filing.get('accession_number')}")
                        continue

                    # Fetch and parse Form 4 XML
                    xml_content = await sec_client.fetch_form4_document(
                        filing["filing_url"]
                    )

                    from app.services.form4_parser import Form4Parser
                    parsed = Form4Parser.parse(xml_content)

                    # Process transactions
                    for txn in parsed.get("transactions", []):
                        trade = await self._create_trade(
                            db, company, parsed, txn, filing
                        )
                        if trade:
                            trades_created += 1

                    filings_processed += 1

                    # Commit after each filing to free memory
                    await db.commit()

                except Exception as e:
                    logger.error(f"Error processing filing {filing.get('accession_number')}: {e}")
                    await db.rollback()
                    continue

            logger.info(
                f"Scraped {company.ticker}: {filings_processed} filings, "
                f"{trades_created} trades created"
            )

            return {
                "success": True,
                "filings_processed": filings_processed,
                "trades_created": trades_created
            }

        except Exception as e:
            logger.error(f"Scrape failed for {ticker or cik}: {e}")
            return {"success": False, "message": str(e)}

    async def _filing_already_processed(
        self,
        db: AsyncSession,
        filing: Dict,
        company_id: int
    ) -> bool:
        """Check if we already have trades from this filing."""
        sec_url = filing.get("filing_url")
        if not sec_url:
            return False

        result = await db.execute(
            select(Trade).where(
                and_(
                    Trade.company_id == company_id,
                    Trade.sec_filing_url == sec_url
                )
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _create_trade(
        self,
        db: AsyncSession,
        company: Company,
        parsed: Dict,
        txn: Dict,
        filing: Dict
    ) -> Optional[Trade]:
        """Create trade record if not exists."""
        # Get or create insider
        owner = parsed.get("reporting_owner", {})
        insider = await self._get_or_create_insider(db, owner)
        if not insider:
            return None

        # Check if trade already exists (by date + insider + shares + type)
        existing = await db.execute(
            select(Trade).where(
                and_(
                    Trade.company_id == company.id,
                    Trade.insider_id == insider.id,
                    Trade.transaction_date == txn["transaction_date"],
                    Trade.shares == txn["shares"],
                    Trade.transaction_type == txn["transaction_type"]
                )
            )
        )
        if existing.scalar_one_or_none():
            return None  # Already have this trade

        # Parse filing date
        filing_date = None
        if filing.get("filing_date"):
            try:
                filing_date_str = filing["filing_date"]
                if "T" in filing_date_str:
                    # ISO format with time
                    filing_date = datetime.fromisoformat(
                        filing_date_str.replace("Z", "+00:00")
                    ).date()
                else:
                    # Just date
                    filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse filing date: {filing.get('filing_date')}: {e}")

        # Create new trade
        trade = Trade(
            company_id=company.id,
            insider_id=insider.id,
            transaction_type=txn["transaction_type"],
            transaction_date=txn["transaction_date"],
            shares=txn["shares"],
            price_per_share=txn.get("price_per_share"),
            total_value=txn.get("total_value"),
            shares_owned_after=txn.get("shares_owned_after"),
            filing_date=filing_date,
            sec_filing_url=filing.get("filing_url"),
        )
        db.add(trade)
        logger.debug(
            f"Created trade: {insider.name} {txn['transaction_type']} "
            f"{txn['shares']} shares of {company.ticker}"
        )
        return trade

    async def _get_or_create_insider(
        self, db: AsyncSession, owner: Dict
    ) -> Optional[Insider]:
        """Get or create insider record."""
        if not owner.get("name"):
            return None

        name = owner["name"].strip()

        # Check if exists by name
        result = await db.execute(
            select(Insider).where(Insider.name == name)
        )
        insider = result.scalar_one_or_none()

        if not insider:
            insider = Insider(
                name=name,
                cik=owner.get("cik"),
                is_director=owner.get("is_director", False),
                is_officer=owner.get("is_officer", False),
                is_ten_percent_owner=owner.get("is_ten_percent_owner", False),
                officer_title=owner.get("officer_title"),
            )
            db.add(insider)
            await db.flush()  # Get ID without full commit
            logger.debug(f"Created new insider: {name}")

        return insider

