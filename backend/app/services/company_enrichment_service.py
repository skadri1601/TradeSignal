"""
Company Enrichment Service for TradeSignal.

Automatically enriches company and insider data when profiles are viewed.
"""
import logging
import httpx
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.company import Company
from app.models.insider import Insider

logger = logging.getLogger(__name__)


class CompanyEnrichmentService:
    """
    Service for enriching company and insider data from SEC and other sources.
    """

    SEC_API_BASE = "https://data.sec.gov"
    SEC_COMPANY_TICKERS = f"{SEC_API_BASE}/files/company_tickers.json"
    SEC_SUBMISSIONS_BASE = f"{SEC_API_BASE}/submissions"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enrich_company(self, company_id: int) -> Optional[Company]:
        """
        Enrich company data from SEC EDGAR if details are missing.

        Args:
            company_id: Company ID to enrich

        Returns:
            Updated company object or None if not found
        """
        # Get company
        result = await self.db.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()

        if not company:
            return None

        # Check if company needs enrichment
        if company.description and company.sector and company.industry:
            logger.info(f"Company {company.ticker} already has details, skipping enrichment")
            return company

        logger.info(f"Enriching company data for {company.ticker}")

        try:
            # Fetch company facts from SEC
            async with httpx.AsyncClient(timeout=30.0) as client:
                # SEC requires a User-Agent header
                headers = {
                    "User-Agent": "TradeSignal trade-signal@example.com"
                }

                # Get company submissions
                cik_padded = company.cik.zfill(10)
                url = f"{self.SEC_SUBMISSIONS_BASE}/CIK{cik_padded}.json"

                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                data = response.json()

                # Extract company information
                if "name" in data and not company.name:
                    company.name = data["name"]

                if "sicDescription" in data and not company.industry:
                    company.industry = data["sicDescription"]

                # Try to get more details from company facts
                facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
                try:
                    facts_response = await client.get(facts_url, headers=headers)
                    if facts_response.status_code == 200:
                        facts_data = facts_response.json()

                        # Extract entity information
                        if "entityName" in facts_data and not company.name:
                            company.name = facts_data["entityName"]

                        # Generate a basic description
                        if not company.description:
                            company.description = (
                                f"{company.name} ({company.ticker}) is a publicly traded company "
                                f"in the {company.industry or 'technology'} industry. "
                                f"CIK: {company.cik}"
                            )

                        # Set sector based on industry (simple mapping)
                        if not company.sector and company.industry:
                            company.sector = self._map_industry_to_sector(company.industry)

                except httpx.HTTPError as e:
                    logger.warning(f"Could not fetch company facts for {company.ticker}: {e}")

                # If still no description, create a basic one
                if not company.description:
                    company.description = (
                        f"{company.name} ({company.ticker}) is a publicly traded company. "
                        f"CIK: {company.cik}"
                    )

                # Set default sector if still missing
                if not company.sector:
                    company.sector = "Technology"

                # Update last_updated timestamp
                from datetime import datetime
                company.updated_at = datetime.utcnow()

                await self.db.commit()
                await self.db.refresh(company)

                logger.info(f"✅ Enriched company {company.ticker}")
                return company

        except httpx.HTTPError as e:
            logger.error(f"Failed to enrich company {company.ticker}: {e}")
            return company
        except Exception as e:
            logger.error(f"Unexpected error enriching company {company.ticker}: {e}")
            return company

    async def enrich_insider(self, insider_id: int) -> Optional[Insider]:
        """
        Enrich insider data from SEC EDGAR if details are missing.

        Args:
            insider_id: Insider ID to enrich

        Returns:
            Updated insider object or None if not found
        """
        # Get insider
        result = await self.db.execute(
            select(Insider).where(Insider.id == insider_id)
        )
        insider = result.scalar_one_or_none()

        if not insider:
            return None

        # Check if insider needs enrichment
        if insider.title and insider.email:
            logger.info(f"Insider {insider.name} already has details, skipping enrichment")
            return insider

        logger.info(f"Enriching insider data for {insider.name} (CIK: {insider.cik})")

        try:
            # Fetch insider data from SEC
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "User-Agent": "TradeSignal trade-signal@example.com"
                }

                # Get insider's filing history
                cik_padded = insider.cik.zfill(10)
                url = f"{self.SEC_SUBMISSIONS_BASE}/CIK{cik_padded}.json"

                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                data = response.json()

                # Extract insider information
                if "name" in data:
                    # Update name if it's more complete
                    sec_name = data["name"]
                    if len(sec_name) > len(insider.name or ""):
                        insider.name = sec_name

                # Try to extract title from recent filings
                if "filings" in data and "recent" in data["filings"]:
                    recent_filings = data["filings"]["recent"]

                    # Look for Form 4 filings
                    if "form" in recent_filings:
                        for i, form in enumerate(recent_filings["form"]):
                            if form == "4":
                                # This is a Form 4 filing
                                # We'll set a generic title since extracting from filings is complex
                                if not insider.title:
                                    insider.title = "Corporate Insider"
                                break

                # Set default title if still missing
                if not insider.title:
                    insider.title = "Corporate Insider"

                # Email is typically not in SEC data, so we'll leave it None

                # Update timestamp
                from datetime import datetime
                insider.updated_at = datetime.utcnow()

                await self.db.commit()
                await self.db.refresh(insider)

                logger.info(f"✅ Enriched insider {insider.name}")
                return insider

        except httpx.HTTPError as e:
            logger.error(f"Failed to enrich insider {insider.name}: {e}")
            return insider
        except Exception as e:
            logger.error(f"Unexpected error enriching insider {insider.name}: {e}")
            return insider

    def _map_industry_to_sector(self, industry: str) -> str:
        """Map SIC industry description to a sector."""
        industry_lower = industry.lower()

        if any(word in industry_lower for word in ["computer", "software", "internet", "technology", "semiconductor"]):
            return "Technology"
        elif any(word in industry_lower for word in ["pharmaceutical", "drug", "biotech", "medical", "health"]):
            return "Healthcare"
        elif any(word in industry_lower for word in ["bank", "finance", "insurance", "investment"]):
            return "Financials"
        elif any(word in industry_lower for word in ["retail", "store", "consumer"]):
            return "Consumer"
        elif any(word in industry_lower for word in ["oil", "gas", "energy", "electric", "utility"]):
            return "Energy"
        elif any(word in industry_lower for word in ["manufacturing", "industrial", "machinery"]):
            return "Industrials"
        elif any(word in industry_lower for word in ["telecom", "communication", "wireless"]):
            return "Communications"
        elif any(word in industry_lower for word in ["real estate", "reit"]):
            return "Real Estate"
        elif any(word in industry_lower for word in ["material", "chemical", "metal", "mining"]):
            return "Materials"
        else:
            return "Other"
