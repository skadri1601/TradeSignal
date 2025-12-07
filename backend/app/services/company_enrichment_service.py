"""
Company Enrichment Service for TradeSignal.

Automatically enriches company and insider data when profiles are viewed.
Uses SEC EDGAR API and Yahoo Finance for comprehensive company data.
"""
import logging
import httpx
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.company import Company
from app.models.insider import Insider
from app.services.company_profile_service import CompanyProfileService

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
        Enrich company data from SEC EDGAR and Yahoo Finance if details are missing.

        Args:
            company_id: Company ID to enrich

        Returns:
            Updated company object or None if not found
        """
        # Get company
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()

        if not company:
            return None

        # Check if company needs enrichment
        # Consider stale if updated more than 7 days ago
        days_since_update = (
            (datetime.utcnow() - company.updated_at).days if company.updated_at else 999
        )
        is_stale = days_since_update > 7

        # Check if critical data is missing
        needs_enrichment = (
            not company.logo_url
            or not company.sector
            or not company.industry
            or not company.market_cap
            or not company.description
            or is_stale
        )

        if not needs_enrichment:
            logger.info(
                f"Company {company.ticker} already has complete data, skipping enrichment"
            )
            return company

        logger.info(f"Enriching company data for {company.ticker} (stale: {is_stale})")

        # First try Yahoo Finance for comprehensive data (logo, sector, industry, market cap)
        profile_service = CompanyProfileService(self.db)
        company = await profile_service.enrich_company_if_needed(company_id)

        # If Yahoo Finance didn't provide everything, try SEC as fallback
        if not company.sector or not company.industry:
            logger.info(
                f"Yahoo Finance incomplete for {company.ticker}, trying SEC EDGAR"
            )
            company = await self._enrich_from_sec(company)

        return company

    async def _enrich_from_sec(self, company: Company) -> Company:
        """
        Enrich company data from SEC EDGAR API.

        Args:
            company: Company model instance

        Returns:
            Updated company instance
        """
        try:
            # Fetch company facts from SEC
            async with httpx.AsyncClient(timeout=30.0) as client:
                # SEC requires a User-Agent header
                headers = {"User-Agent": "TradeSignal trade-signal@example.com"}

                # Get company submissions
                cik_padded = company.cik.zfill(10)
                url = f"{self.SEC_SUBMISSIONS_BASE}/CIK{cik_padded}.json"

                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                data = response.json()

                updated = False

                # Extract company information
                if "name" in data and (
                    not company.name or len(data["name"]) > len(company.name or "")
                ):
                    company.name = data["name"]
                    updated = True

                if "sicDescription" in data and not company.industry:
                    company.industry = data["sicDescription"]
                    updated = True

                # Try to get more details from company facts
                facts_url = (
                    f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
                )
                try:
                    facts_response = await client.get(facts_url, headers=headers)
                    if facts_response.status_code == 200:
                        facts_data = facts_response.json()

                        # Extract entity information
                        if "entityName" in facts_data and (
                            not company.name
                            or len(facts_data["entityName"]) > len(company.name or "")
                        ):
                            company.name = facts_data["entityName"]
                            updated = True

                        # Generate a basic description
                        if not company.description:
                            company.description = (
                                f"{company.name} ({company.ticker}) is a publicly traded company "
                                f"in the {company.industry or 'technology'} industry. "
                                f"CIK: {company.cik}"
                            )
                            updated = True

                        # Set sector based on industry (simple mapping)
                        if not company.sector and company.industry:
                            company.sector = self._map_industry_to_sector(
                                company.industry
                            )
                            updated = True

                except httpx.HTTPError as e:
                    logger.warning(
                        f"Could not fetch company facts for {company.ticker}: {e}"
                    )

                # If still no description, create a basic one
                if not company.description:
                    company.description = (
                        f"{company.name} ({company.ticker}) is a publicly traded company. "
                        f"CIK: {company.cik}"
                    )
                    updated = True

                # Set default sector if still missing
                if not company.sector:
                    company.sector = "Technology"
                    updated = True

                if updated:
                    # Update last_updated timestamp
                    company.updated_at = datetime.utcnow()
                    await self.db.commit()
                    await self.db.refresh(company)
                    logger.info(f"✅ Enriched company {company.ticker} from SEC")

        except httpx.HTTPError as e:
            logger.error(f"Failed to enrich company {company.ticker} from SEC: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error enriching company {company.ticker} from SEC: {e}"
            )

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
        result = await self.db.execute(select(Insider).where(Insider.id == insider_id))
        insider = result.scalar_one_or_none()

        if not insider:
            return None

        # Check if insider needs enrichment
        if insider.title:
            logger.info(
                f"Insider {insider.name} already has details, skipping enrichment"
            )
            return insider

        logger.info(f"Enriching insider data for {insider.name}")

        # Insiders don't have CIK, skip SEC API enrichment for now
        # TODO: Implement insider-specific enrichment if needed
        return insider

        try:
            # Fetch insider data from SEC
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"User-Agent": "TradeSignal trade-signal@example.com"}

                # Note: Insiders don't have CIK numbers, companies do
                # This section needs to be refactored
                url = None

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

        if any(
            word in industry_lower
            for word in [
                "computer",
                "software",
                "internet",
                "technology",
                "semiconductor",
            ]
        ):
            return "Technology"
        elif any(
            word in industry_lower
            for word in ["pharmaceutical", "drug", "biotech", "medical", "health"]
        ):
            return "Healthcare"
        elif any(
            word in industry_lower
            for word in ["bank", "finance", "insurance", "investment"]
        ):
            return "Financials"
        elif any(word in industry_lower for word in ["retail", "store", "consumer"]):
            return "Consumer"
        elif any(
            word in industry_lower
            for word in ["oil", "gas", "energy", "electric", "utility"]
        ):
            return "Energy"
        elif any(
            word in industry_lower
            for word in ["manufacturing", "industrial", "machinery"]
        ):
            return "Industrials"
        elif any(
            word in industry_lower for word in ["telecom", "communication", "wireless"]
        ):
            return "Communications"
        elif any(word in industry_lower for word in ["real estate", "reit"]):
            return "Real Estate"
        elif any(
            word in industry_lower
            for word in ["material", "chemical", "metal", "mining"]
        ):
            return "Materials"
        else:
            return "Other"
