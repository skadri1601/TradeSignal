from app.core.celery_app import celery_app
import logging
import httpx
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import asyncio

from app.config import settings
from app.models.company import Company
from app.services.company_profile_service import CompanyProfileService # Still needed for Yahoo Finance part of enrichment
from app.database import db_manager # For session in Celery task

logger = logging.getLogger(__name__)

# Helper function to map industry to sector (moved from service)
def _map_industry_to_sector(industry: str) -> str:
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
        word in industry_lower
        for word in ["telecom", "communication", "wireless"]
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


async def _enrich_from_sec(db: AsyncSession, company: Company) -> Company:
    """
    Internal function to enrich company data from SEC EDGAR API.
    This logic is moved from the service to be called within the Celery task.
    """
    SEC_API_BASE = "https://data.sec.gov"
    SEC_SUBMISSIONS_BASE = f"{SEC_API_BASE}/submissions"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"User-Agent": settings.sec_user_agent} # Use global SEC user agent

            # Get company submissions
            cik_padded = company.cik.zfill(10)
            url = f"{SEC_SUBMISSIONS_BASE}/CIK{cik_padded}.json"

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
                        company.sector = _map_industry_to_sector(
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
                await db.commit()
                await db.refresh(company)
                logger.info(f"✅ Enriched company {company.ticker} from SEC")

    except httpx.HTTPError as e:
        logger.error(f"Failed to enrich company {company.ticker} from SEC: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected error enriching company {company.ticker} from SEC: {e}"
        )

    return company


@celery_app.task(name="enrich_company_profile")
def enrich_company_profile_task(company_id: int):
    """
    Celery task to enrich a company's profile data from external sources.
    This task consolidates enrichment from CompanyProfileService (Yahoo) and SEC.
    """
    async def _async_task():
        logger.info(f"Starting enrich_company_profile_task for company ID: {company_id}")
        async with db_manager.get_session() as db:
            result = await db.execute(select(Company).where(Company.id == company_id))
            company = result.scalar_one_or_none()

            if not company:
                logger.warning(f"Company with ID {company_id} not found for enrichment.")
                return

            original_updated_at = company.updated_at
            
            # --- 1. Enrich from CompanyProfileService (Yahoo Finance) ---
            # Note: CompanyProfileService still takes a DB session for its own operations
            profile_service = CompanyProfileService(db)
            try:
                company = await profile_service.enrich_company_if_needed(company.id)
                if company and company.updated_at != original_updated_at:
                    logger.info(f"Company {company.ticker} enriched by CompanyProfileService (Yahoo).")
                    original_updated_at = company.updated_at
            except Exception as e:
                logger.error(f"Error enriching company {company.ticker} from CompanyProfileService: {e}", exc_info=True)


            # --- 2. Enrich from SEC EDGAR (if needed) ---
            # Check if critical data is still missing after Yahoo enrichment
            needs_sec_enrichment = (
                not company.sector
                or not company.industry
                or not company.description
            )

            if needs_sec_enrichment and company.cik:
                logger.info(f"Company {company.ticker} still needs SEC enrichment.")
                try:
                    company = await _enrich_from_sec(db, company)
                    if company and company.updated_at != original_updated_at:
                         logger.info(f"Company {company.ticker} enriched by SEC EDGAR.")
                except Exception as e:
                    logger.error(f"Error enriching company {company.ticker} from SEC: {e}", exc_info=True)
            else:
                logger.debug(f"Company {company.ticker} does not need SEC enrichment or CIK is missing.")
                
            # Final update to timestamp if any changes were made within this task.
            # This is handled by each _enrich function if they commit.
            # But we ensure the overall 'updated_at' is current.
            company.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(company)
            logger.info(f"Finished enrich_company_profile_task for company ID: {company_id}.")
    
    asyncio.run(_async_task())

@celery_app.task(name="enrich_all_companies_profile")
def enrich_all_companies_profile_task():
    """
    Orchestrator task to enrich profile data for all companies in the database.
    This should be scheduled periodically.
    """
    async def _async_task():
        logger.info("Starting enrich_all_companies_profile_task...")
        async with db_manager.get_session() as db:
            # Fetch companies that need enrichment (e.g., missing key fields or stale data)
            # For simplicity, initially enqueue all, but can optimize later.
            companies_to_enrich = await db.execute(
                select(Company).filter(
                    (Company.cik.isnot(None)) # Only enrich if we have a CIK
                )
            )
            companies = companies_to_enrich.scalars().all()

            for company in companies:
                # Check for staleness to avoid enriching already fresh companies
                days_since_update = (
                    (datetime.utcnow() - company.updated_at).days if company.updated_at else settings.company_enrichment_stale_days + 1
                )
                is_stale = days_since_update > settings.company_enrichment_stale_days
                
                needs_enrichment = (
                    not company.logo_url
                    or not company.sector
                    or not company.industry
                    or not company.market_cap
                    or not company.description
                    or is_stale
                )
                
                if needs_enrichment:
                    logger.debug(f"Enqueuing enrichment for company: {company.name} (ID: {company.id}, Ticker: {company.ticker})")
                    enrich_company_profile_task.delay(company.id)
                else:
                    logger.debug(f"Company {company.name} (ID: {company.id}) is already enriched and not stale. Skipping.")
                    
        logger.info("Finished enqueueing company profile enrichment tasks.")
    
    asyncio.run(_async_task())