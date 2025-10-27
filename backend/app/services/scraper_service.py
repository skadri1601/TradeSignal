"""
SEC Form 4 Scraper Service

Orchestrates fetching Form 4 filings from SEC and saving to database.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.company import Company
from app.models.insider import Insider
from app.models.trade import Trade
from app.services.sec_client import SECClient
from app.services.form4_parser import Form4Parser
from app.schemas.company import CompanyCreate
from app.schemas.insider import InsiderCreate
from app.schemas.trade import TradeCreate

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping insider trades from SEC EDGAR."""

    def __init__(self, sec_client: Optional[SECClient] = None):
        """
        Initialize scraper service.

        Args:
            sec_client: SEC client instance (creates new if None)
        """
        self.sec_client = sec_client or SECClient()

    async def scrape_company_trades(
        self,
        db: AsyncSession,
        ticker: Optional[str] = None,
        cik: Optional[str] = None,
        days_back: int = 30,
        max_filings: int = 100
    ) -> Dict[str, Any]:
        """
        Scrape Form 4 filings for a specific company.

        Args:
            db: Database session
            ticker: Company ticker symbol
            cik: Company CIK
            days_back: How many days back to fetch
            max_filings: Maximum number of filings to process

        Returns:
            Summary of scraping results
        """
        if not ticker and not cik:
            raise ValueError("Must provide either ticker or CIK")

        logger.info(f"Starting scrape for {ticker or cik} (last {days_back} days)")

        # If ticker provided, try to get CIK from database first (SEC prefers CIK)
        if ticker and not cik:
            result = await db.execute(
                select(Company).where(Company.ticker == ticker.upper())
            )
            company = result.scalar_one_or_none()
            if company and company.cik:
                cik = company.cik
                logger.info(f"Found CIK {cik} for ticker {ticker} in database")

        start_date = datetime.now() - timedelta(days=days_back)

        # Fetch Form 4 filings from SEC
        try:
            filings = await self.sec_client.fetch_recent_form4_filings(
                cik=cik,
                ticker=ticker,
                start_date=start_date,
                count=max_filings
            )
        except Exception as e:
            logger.error(f"Failed to fetch Form 4 filings: {e}")
            return {
                "success": False,
                "error": str(e),
                "filings_processed": 0,
                "trades_created": 0
            }

        if not filings:
            logger.info("No Form 4 filings found")
            return {
                "success": True,
                "filings_processed": 0,
                "trades_created": 0,
                "message": "No filings found"
            }

        # Process each filing
        trades_created = 0
        filings_processed = 0
        errors = []

        for filing in filings[:max_filings]:
            try:
                created_count = await self._process_filing(db, filing)
                trades_created += created_count
                filings_processed += 1

            except Exception as e:
                logger.error(f"Failed to process filing {filing.get('accession_number')}: {e}")
                errors.append(str(e))
                continue

        logger.info(
            f"Scrape complete: {filings_processed} filings, "
            f"{trades_created} trades created"
        )

        return {
            "success": True,
            "filings_processed": filings_processed,
            "trades_created": trades_created,
            "errors": errors if errors else None
        }

    async def _process_filing(self, db: AsyncSession, filing: Dict[str, Any]) -> int:
        """
        Process a single Form 4 filing.

        Args:
            db: Database session
            filing: Filing metadata from SEC

        Returns:
            Number of trades created
        """
        filing_url = filing.get("filing_url")
        if not filing_url:
            logger.warning("Filing has no URL, skipping")
            return 0

        # Fetch the actual Form 4 XML document
        try:
            xml_content = await self.sec_client.fetch_form4_document(filing_url)
        except Exception as e:
            logger.error(f"Failed to fetch Form 4 document: {e}")
            return 0

        # Parse Form 4 XML
        try:
            parsed_data = Form4Parser.parse(xml_content)
        except Exception as e:
            logger.error(f"Failed to parse Form 4: {e}")
            return 0

        # Ensure company exists
        company = await self._ensure_company(db, parsed_data["issuer"])
        if not company:
            logger.warning(f"Could not create/find company: {parsed_data['issuer']}")
            return 0

        # Ensure insider exists
        insider = await self._ensure_insider(
            db,
            parsed_data["reporting_owner"],
            company.id
        )
        if not insider:
            logger.warning(f"Could not create/find insider: {parsed_data['reporting_owner']}")
            return 0

        # Create trades
        trades_created = 0
        for txn in parsed_data["transactions"]:
            try:
                trade = await self._create_trade(
                    db,
                    txn,
                    company.id,
                    insider.id,
                    filing_url
                )
                if trade:
                    trades_created += 1

            except IntegrityError:
                # Duplicate trade, skip
                await db.rollback()
                logger.debug("Duplicate trade detected, skipping")
                continue

            except Exception as e:
                logger.error(f"Failed to create trade: {e}")
                await db.rollback()
                continue

        return trades_created

    async def _ensure_company(
        self,
        db: AsyncSession,
        issuer_data: Dict[str, str]
    ) -> Optional[Company]:
        """
        Ensure company exists in database, create if not.

        Args:
            db: Database session
            issuer_data: Issuer info from Form 4

        Returns:
            Company instance or None
        """
        cik = issuer_data.get("cik")
        if not cik:
            return None

        # Check if exists
        result = await db.execute(
            select(Company).where(Company.cik == cik)
        )
        company = result.scalar_one_or_none()

        if company:
            return company

        # Create new company
        try:
            company_data = CompanyCreate(
                ticker=issuer_data.get("ticker", "UNKNOWN"),
                name=issuer_data.get("name", "Unknown Company"),
                cik=cik
            )

            company = Company(**company_data.model_dump())
            db.add(company)
            await db.commit()
            await db.refresh(company)

            logger.info(f"Created company: {company.ticker} (CIK: {company.cik})")
            return company

        except IntegrityError:
            await db.rollback()
            # Race condition: company was created by another process
            result = await db.execute(
                select(Company).where(Company.cik == cik)
            )
            return result.scalar_one_or_none()

    async def _ensure_insider(
        self,
        db: AsyncSession,
        owner_data: Dict[str, Any],
        company_id: int
    ) -> Optional[Insider]:
        """
        Ensure insider exists in database, create if not.

        Args:
            db: Database session
            owner_data: Reporting owner info from Form 4
            company_id: Associated company ID

        Returns:
            Insider instance or None
        """
        name = owner_data.get("name")
        if not name:
            return None

        # Check if exists (by name and company)
        result = await db.execute(
            select(Insider).where(
                Insider.name == name,
                Insider.company_id == company_id
            )
        )
        insider = result.scalar_one_or_none()

        if insider:
            return insider

        # Create new insider
        try:
            insider_data = InsiderCreate(
                name=name,
                title=owner_data.get("officer_title"),
                relationship=owner_data.get("other_text"),
                company_id=company_id,
                is_director=owner_data.get("is_director", False),
                is_officer=owner_data.get("is_officer", False),
                is_ten_percent_owner=owner_data.get("is_ten_percent_owner", False),
                is_other=owner_data.get("is_other", False)
            )

            insider = Insider(**insider_data.model_dump())
            db.add(insider)
            await db.commit()
            await db.refresh(insider)

            logger.info(f"Created insider: {insider.name}")
            return insider

        except IntegrityError:
            await db.rollback()
            # Race condition
            result = await db.execute(
                select(Insider).where(
                    Insider.name == name,
                    Insider.company_id == company_id
                )
            )
            return result.scalar_one_or_none()

    async def _create_trade(
        self,
        db: AsyncSession,
        txn_data: Dict[str, Any],
        company_id: int,
        insider_id: int,
        filing_url: str
    ) -> Optional[Trade]:
        """
        Create a trade from transaction data.

        Args:
            db: Database session
            txn_data: Transaction data from Form 4
            company_id: Company ID
            insider_id: Insider ID
            filing_url: SEC filing URL

        Returns:
            Created Trade instance or None
        """
        try:
            # Parse filing date from URL or use today
            filing_date = datetime.now().date()

            trade_data = TradeCreate(
                insider_id=insider_id,
                company_id=company_id,
                transaction_date=txn_data["transaction_date"],
                filing_date=filing_date,
                transaction_type=txn_data["transaction_type"],
                transaction_code=txn_data.get("transaction_code", ""),
                shares=txn_data["shares"],
                price_per_share=txn_data.get("price_per_share"),
                total_value=txn_data.get("total_value"),
                shares_owned_after=txn_data.get("shares_owned_after"),
                ownership_type=txn_data.get("ownership_type", "Direct"),
                derivative_transaction=txn_data.get("derivative_transaction", False),
                sec_filing_url=filing_url
            )

            trade = Trade(**trade_data.model_dump())
            db.add(trade)
            await db.commit()
            await db.refresh(trade)

            logger.debug(
                f"Created trade: {trade.transaction_type} "
                f"{trade.shares} shares @ ${trade.price_per_share}"
            )

            return trade

        except Exception as e:
            logger.error(f"Failed to create trade: {e}")
            await db.rollback()
            return None
