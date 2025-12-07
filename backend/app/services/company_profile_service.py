"""
Company Profile Service for TradeSignal.

Fetches company profile data from Yahoo Finance including:
- Logo URLs
- Sector and industry
- Market cap
- Company description
"""

import logging
import yfinance as yf
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.company import Company

logger = logging.getLogger(__name__)


class CompanyProfileService:
    """
    Service for fetching company profile data from Yahoo Finance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_company_logo(self, ticker: str) -> Optional[str]:
        """
        Get company logo URL from Yahoo Finance.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Logo URL or None if not found
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Yahoo Finance provides logo URL in the 'logo_url' field
            logo_url = info.get("logo_url")
            if logo_url:
                logger.info(f"Found logo for {ticker}: {logo_url}")
                return logo_url

            logger.warning(f"No logo URL found for {ticker}")
            return None

        except Exception as e:
            logger.error(f"Error fetching logo for {ticker}: {e}")
            return None

    async def enrich_company_if_needed(self, company_id: int) -> Optional[Company]:
        """
        Enrich company data from Yahoo Finance if details are missing.

        Fetches:
        - Logo URL
        - Sector
        - Industry
        - Market cap
        - Description

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

        try:
            stock = yf.Ticker(company.ticker)
            info = stock.info

            updated = False

            # Get logo URL
            if not company.logo_url:
                logo_url = info.get("logo_url")
                if logo_url:
                    company.logo_url = logo_url
                    updated = True
                    logger.info(f"Updated logo for {company.ticker}")

            # Get sector
            if not company.sector:
                sector = info.get("sector")
                if sector:
                    company.sector = sector
                    updated = True
                    logger.info(f"Updated sector for {company.ticker}: {sector}")

            # Get industry
            if not company.industry:
                industry = info.get("industry")
                if industry:
                    company.industry = industry
                    updated = True
                    logger.info(f"Updated industry for {company.ticker}: {industry}")

            # Get market cap
            if not company.market_cap:
                market_cap = info.get("marketCap")
                if market_cap:
                    company.market_cap = int(market_cap)
                    updated = True
                    logger.info(f"Updated market cap for {company.ticker}")

            # Get description
            if not company.description:
                description = info.get("longBusinessSummary") or info.get(
                    "longDescription"
                )
                if description:
                    # Truncate if too long (database field might have limit)
                    if len(description) > 5000:
                        description = description[:5000]
                    company.description = description
                    updated = True
                    logger.info(f"Updated description for {company.ticker}")

            # Update name if more complete
            if info.get("longName") and (
                not company.name or len(info["longName"]) > len(company.name or "")
            ):
                company.name = info["longName"]
                updated = True

            # Update website if available
            if not company.website and info.get("website"):
                company.website = info["website"]
                updated = True

            if updated:
                company.updated_at = datetime.utcnow()
                await self.db.commit()
                await self.db.refresh(company)
                logger.info(f"✅ Enriched company {company.ticker} from Yahoo Finance")

        except Exception as e:
            logger.error(
                f"Error enriching company {company.ticker} from Yahoo Finance: {e}"
            )

        return company
