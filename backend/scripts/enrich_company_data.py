"""
Enrich company data with sector, industry, and market cap information.

Uses Yahoo Finance data via yfinance library to populate missing company details.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_manager
from app.models import Company
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)


async def enrich_company_data():
    """Fetch and update company sector, industry, and market cap data."""

    async with db_manager.get_session() as session:
        # Get all companies
        result = await session.execute(select(Company))
        companies = result.scalars().all()

        print(f"\nFound {len(companies)} companies to enrich\n")
        print("=" * 80)

        updated_count = 0
        failed_count = 0

        for company in companies:
            ticker = company.ticker
            print(f"\nProcessing {ticker} - {company.name}...")

            try:
                # Fetch data from Yahoo Finance with retry logic
                stock = yf.Ticker(ticker)

                # Add delay before request
                await asyncio.sleep(1.0)

                info = stock.info

                # Check if we got rate limited
                if not info or len(info) < 5:
                    print(f"  ⚠ Limited data received, skipping...")
                    continue

                # Extract relevant fields
                sector = info.get('sector')
                industry = info.get('industry')
                market_cap = info.get('marketCap')
                website = info.get('website')
                description = info.get('longBusinessSummary')

                # Update company record
                if sector:
                    company.sector = sector
                if industry:
                    company.industry = industry
                if market_cap:
                    company.market_cap = float(market_cap)
                if website:
                    company.website = website
                if description:
                    # Limit description to 500 characters
                    company.description = description[:500]

                await session.commit()

                print(f"  ✓ Updated:")
                print(f"    Sector: {sector or 'N/A'}")
                print(f"    Industry: {industry or 'N/A'}")
                print(f"    Market Cap: ${market_cap:,}" if market_cap else "    Market Cap: N/A")

                updated_count += 1

                # Rate limiting - be nice to Yahoo Finance
                await asyncio.sleep(2.0)  # Increased delay to avoid rate limiting

            except Exception as e:
                print(f"  ✗ Failed: {str(e)}")
                failed_count += 1
                continue

        print("\n" + "=" * 80)
        print(f"\nSummary:")
        print(f"  Total Companies: {len(companies)}")
        print(f"  Successfully Updated: {updated_count}")
        print(f"  Failed: {failed_count}")
        print("\n" + "=" * 80)


async def main():
    """Main entry point."""
    print("=" * 80)
    print("TradeSignal - Company Data Enrichment")
    print("=" * 80)
    print("\nThis script will fetch sector, industry, and market cap data")
    print("from Yahoo Finance for all companies in the database.\n")

    try:
        await enrich_company_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n✅ Company data enrichment complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
