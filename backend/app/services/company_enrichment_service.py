"""
Company Enrichment Service for TradeSignal.

Automatically enriches company and insider data when profiles are viewed.
Uses Celery tasks to fetch data from SEC EDGAR API and Yahoo Finance asynchronously.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.company import Company
from app.models.insider import Insider
from app.config import settings
from app.tasks.enrichment_tasks import enrich_company_profile_task

logger = logging.getLogger(__name__)


class CompanyEnrichmentService:
    """
    Service for enriching company and insider data via background tasks.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enrich_company(self, company_id: int) -> Optional[Company]:
        """
        Check if company data needs enrichment and enqueue a background task if so.

        Args:
            company_id: Company ID to enrich

        Returns:
            Company object (potentially not yet enriched)
        """
        # Get company
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()

        if not company:
            return None

        # Check if company needs enrichment
        # Consider stale if updated more than configured days ago (default 7)
        stale_days = getattr(settings, "company_enrichment_stale_days", 7)
        days_since_update = (
            (datetime.utcnow() - company.updated_at).days if company.updated_at else stale_days + 1
        )
        is_stale = days_since_update > stale_days

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
            logger.debug(
                f"Company {company.ticker} already has complete data, skipping enrichment"
            )
            return company

        logger.info(f"Enqueuing company enrichment task for {company.ticker} (stale: {is_stale})")

        # Enqueue the Celery task
        enrich_company_profile_task.delay(company_id)

        # Return the current company object immediately
        # The frontend will eventually see updated data via polling or subsequent requests
        return company

    async def enrich_insider(self, insider_id: int) -> Optional[Insider]:
        """
        Enrich insider data if details are missing.
        Currently a placeholder as insider enrichment is less critical/available.

        Args:
            insider_id: Insider ID to enrich

        Returns:
            Insider object
        """
        # Get insider
        result = await self.db.execute(select(Insider).where(Insider.id == insider_id))
        insider = result.scalar_one_or_none()

        if not insider:
            return None

        # Logic for insider enrichment can be added here later, likely also via a background task.
        return insider
