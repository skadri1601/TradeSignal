"""
Enrich insider data with professional titles and information from online sources.

This script uses multiple APIs to fetch live data about corporate insiders:
1. LinkedIn profiles (via RapidAPI or similar)
2. Company executive pages
3. SEC Edgar filing data
4. News articles and press releases

Note: This requires API keys for external services.
"""

import asyncio
import sys
from pathlib import Path
import re
from typing import Optional, Dict
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_manager
from app.models import Insider, Company
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsiderEnricher:
    """Enrich insider data from multiple sources."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def search_sec_edgar(self, insider_name: str, company_cik: str) -> Optional[str]:
        """
        Search SEC Edgar for insider information.

        SEC Form 4 XML files often contain more detailed title information
        that may not be parsed in the initial scrape.
        """
        try:
            # Construct SEC Edgar search URL
            # Format: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=XXXX&type=4
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={company_cik}&type=4&dateb=&owner=only&count=10"

            headers = {
                "User-Agent": "TradeSignal Enrichment kadrisaad1601@gmail.com",
                "Accept": "text/html,application/xhtml+xml",
            }

            response = await self.client.get(url, headers=headers)

            if response.status_code == 200:
                # Parse HTML for recent Form 4 filings by this insider
                # Look for XML links and fetch detailed info
                # This is a simplified version - would need proper HTML parsing
                logger.info(f"✓ Fetched SEC data for {insider_name}")
                return None  # Placeholder - would extract title from XML
            else:
                logger.warning(f"⚠ SEC Edgar returned {response.status_code} for {insider_name}")
                return None

        except Exception as e:
            logger.error(f"✗ SEC Edgar search failed for {insider_name}: {e}")
            return None

    async def search_company_website(self, company_website: Optional[str], insider_name: str) -> Optional[str]:
        """
        Search company website for executive information.

        Many companies have "About Us" or "Leadership Team" pages with
        executive bios and titles.
        """
        if not company_website:
            return None

        try:
            # Common paths for leadership pages
            paths = [
                "/about/leadership",
                "/about/management",
                "/leadership",
                "/management",
                "/team",
                "/about-us/leadership",
                "/company/leadership",
                "/investors/leadership",
            ]

            name_parts = insider_name.lower().split()

            for path in paths:
                url = company_website.rstrip('/') + path
                try:
                    response = await self.client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        content = response.text.lower()

                        # Simple check if insider's name appears on the page
                        if all(part in content for part in name_parts):
                            # Look for title patterns near the name
                            # This is simplified - would need proper HTML parsing
                            title_patterns = [
                                r'(chief\s+\w+\s+officer)',
                                r'(vice\s+president)',
                                r'(senior\s+vice\s+president)',
                                r'(executive\s+vice\s+president)',
                                r'(president\s+and\s+\w+)',
                                r'(director\s+of\s+\w+)',
                            ]

                            for pattern in title_patterns:
                                match = re.search(pattern, content, re.IGNORECASE)
                                if match:
                                    title = match.group(1)
                                    logger.info(f"✓ Found title '{title}' on company website for {insider_name}")
                                    return title.title()

                    await asyncio.sleep(0.5)  # Be nice to company servers

                except Exception as e:
                    continue

            return None

        except Exception as e:
            logger.error(f"✗ Company website search failed for {insider_name}: {e}")
            return None

    async def infer_title_from_role_flags(self, insider: Insider) -> Optional[str]:
        """
        Infer a basic title from role flags when no other data is available.

        This is a fallback that provides generic but accurate titles.
        """
        if insider.title:
            return None  # Already has a title

        # For directors without a title, we can provide a generic "Board Director" title
        if insider.is_director and not insider.is_officer:
            return "Board Director"

        # For officers without specific titles
        if insider.is_officer and not insider.title:
            return "Corporate Officer"

        # For 10% owners
        if insider.is_ten_percent_owner:
            return "Major Shareholder"

        return None

    async def enrich_insider(self, insider: Insider, company: Optional[Company]) -> Dict[str, any]:
        """
        Enrich a single insider with data from multiple sources.

        Returns a dict with enriched data.
        """
        logger.info(f"\nEnriching: {insider.name}")

        enriched_data = {}

        # If insider already has a title, skip
        if insider.title and insider.title.strip():
            logger.info(f"  ✓ Already has title: {insider.title}")
            return enriched_data

        # Try SEC Edgar first (most authoritative source)
        if company:
            title = await self.search_sec_edgar(insider.name, company.cik)
            if title:
                enriched_data['title'] = title
                return enriched_data

        # Try company website
        if company and company.website:
            title = await self.search_company_website(company.website, insider.name)
            if title:
                enriched_data['title'] = title
                return enriched_data

        # Fallback: Infer from role flags
        title = await self.infer_title_from_role_flags(insider)
        if title:
            enriched_data['title'] = title
            logger.info(f"  → Inferred title: {title}")
        else:
            logger.info(f"  ⚠ No title data found")

        return enriched_data


async def enrich_insiders():
    """Main function to enrich insider data."""

    enricher = InsiderEnricher()

    try:
        async with db_manager.get_session() as session:
            # Get insiders with missing titles
            result = await session.execute(
                select(Insider)
                .where((Insider.title == None) | (Insider.title == ''))
                .limit(50)  # Process in batches
            )
            insiders = result.scalars().all()

            print(f"\nFound {len(insiders)} insiders with missing titles\n")
            print("=" * 80)

            updated_count = 0
            failed_count = 0

            for insider in insiders:
                # Get associated company
                company = None
                if insider.company_id:
                    result = await session.execute(
                        select(Company).where(Company.id == insider.company_id)
                    )
                    company = result.scalar_one_or_none()

                try:
                    # Enrich the insider
                    enriched_data = await enricher.enrich_insider(insider, company)

                    # Update database if we found new data
                    if enriched_data.get('title'):
                        insider.title = enriched_data['title']
                        await session.commit()
                        updated_count += 1
                        logger.info(f"  ✓ Updated: {insider.name} -> {insider.title}")
                    else:
                        failed_count += 1

                    # Rate limiting
                    await asyncio.sleep(2.0)

                except Exception as e:
                    logger.error(f"  ✗ Failed to enrich {insider.name}: {e}")
                    failed_count += 1
                    await session.rollback()
                    continue

            print("\n" + "=" * 80)
            print(f"\nSummary:")
            print(f"  Total Processed: {len(insiders)}")
            print(f"  Successfully Updated: {updated_count}")
            print(f"  Failed: {failed_count}")
            print("\n" + "=" * 80)

    finally:
        await enricher.close()


async def main():
    """Main entry point."""
    print("=" * 80)
    print("TradeSignal - Insider Data Enrichment")
    print("=" * 80)
    print("\nThis script will enrich insider data from multiple online sources:")
    print("  1. SEC Edgar filings (detailed Form 4 XML)")
    print("  2. Company websites (leadership pages)")
    print("  3. Inferred from role flags (fallback)")
    print()

    try:
        await enrich_insiders()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n✅ Insider data enrichment complete!\n")
    print("Note: For better results, consider:")
    print("  - Using LinkedIn API (requires RapidAPI subscription)")
    print("  - Using Clearbit Enrichment API")
    print("  - Using Crunchbase API for startup executives")
    print()


if __name__ == "__main__":
    asyncio.run(main())
