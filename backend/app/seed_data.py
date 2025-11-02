"""
Seed database with sample data for testing.

⚠️ WARNING: This script is for DEVELOPMENT/TESTING ONLY!
⚠️ DO NOT run this in production - it will create dummy data!

Run this script to populate the database with test companies, insiders, and trades.
"""

import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
import logging

from app.database import db_manager
from app.models import Company, Insider, Trade
from app.services import CompanyService, InsiderService, TradeService
from app.schemas.company import CompanyCreate
from app.schemas.insider import InsiderCreate
from app.schemas.trade import TradeCreate
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample companies data
SAMPLE_COMPANIES = [
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "cik": "0000320193",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": 3000000000000,  # $3T
        "website": "https://www.apple.com"
    },
    {
        "ticker": "TSLA",
        "name": "Tesla Inc.",
        "cik": "0001318605",
        "sector": "Automotive",
        "industry": "Electric Vehicles",
        "market_cap": 800000000000,  # $800B
        "website": "https://www.tesla.com"
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "cik": "0000789019",
        "sector": "Technology",
        "industry": "Software",
        "market_cap": 2800000000000,  # $2.8T
        "website": "https://www.microsoft.com"
    },
    {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "cik": "0001045810",
        "sector": "Technology",
        "industry": "Semiconductors",
        "market_cap": 1200000000000,  # $1.2T
        "website": "https://www.nvidia.com"
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "cik": "0001652044",
        "sector": "Technology",
        "industry": "Internet Services",
        "market_cap": 1700000000000,  # $1.7T
        "website": "https://www.google.com"
    },
]

# Sample insiders for each company
SAMPLE_INSIDERS = [
    # Apple insiders
    {
        "name": "Timothy D. Cook",
        "title": "Chief Executive Officer",
        "ticker": "AAPL",
        "is_director": True,
        "is_officer": True
    },
    {
        "name": "Luca Maestri",
        "title": "Chief Financial Officer",
        "ticker": "AAPL",
        "is_officer": True
    },
    # Tesla insiders
    {
        "name": "Elon Musk",
        "title": "Chief Executive Officer",
        "ticker": "TSLA",
        "is_director": True,
        "is_officer": True,
        "is_ten_percent_owner": True
    },
    {
        "name": "Zachary Kirkhorn",
        "title": "Chief Financial Officer",
        "ticker": "TSLA",
        "is_officer": True
    },
    # Microsoft insiders
    {
        "name": "Satya Nadella",
        "title": "Chief Executive Officer",
        "ticker": "MSFT",
        "is_director": True,
        "is_officer": True
    },
    {
        "name": "Amy Hood",
        "title": "Chief Financial Officer",
        "ticker": "MSFT",
        "is_officer": True
    },
    # NVIDIA insiders
    {
        "name": "Jensen Huang",
        "title": "Chief Executive Officer",
        "ticker": "NVDA",
        "is_director": True,
        "is_officer": True
    },
    # Google insiders
    {
        "name": "Sundar Pichai",
        "title": "Chief Executive Officer",
        "ticker": "GOOGL",
        "is_director": True,
        "is_officer": True
    },
]


async def seed_database():
    """Seed the database with sample data."""
    logger.info("=" * 60)
    logger.info("Starting database seeding...")
    logger.info("=" * 60)

    async with db_manager.get_session() as db:
        # Create companies
        logger.info("\n1. Creating companies...")
        companies_map = {}
        for company_data in SAMPLE_COMPANIES:
            try:
                company = await CompanyService.get_or_create(
                    db=db,
                    ticker=company_data["ticker"],
                    cik=company_data["cik"],
                    name=company_data["name"]
                )

                # Update additional fields
                company.sector = company_data.get("sector")
                company.industry = company_data.get("industry")
                company.market_cap = company_data.get("market_cap")
                company.website = company_data.get("website")

                await db.commit()
                await db.refresh(company)

                companies_map[company_data["ticker"]] = company
                logger.info(f"   ✓ Created/Updated: {company.ticker} - {company.name}")
            except Exception as e:
                logger.error(f"   ✗ Error creating company {company_data['ticker']}: {e}")

        # Create insiders
        logger.info("\n2. Creating insiders...")
        insiders_list = []
        for insider_data in SAMPLE_INSIDERS:
            try:
                ticker = insider_data["ticker"]
                company = companies_map.get(ticker)

                if not company:
                    logger.warning(f"   ⚠ Company {ticker} not found for insider {insider_data['name']}")
                    continue

                insider = await InsiderService.get_or_create(
                    db=db,
                    name=insider_data["name"],
                    company_id=company.id,
                    title=insider_data.get("title"),
                    is_director=insider_data.get("is_director", False),
                    is_officer=insider_data.get("is_officer", False),
                    is_ten_percent_owner=insider_data.get("is_ten_percent_owner", False)
                )

                insiders_list.append(insider)
                logger.info(f"   ✓ Created/Updated: {insider.name} ({company.ticker})")
            except Exception as e:
                logger.error(f"   ✗ Error creating insider {insider_data['name']}: {e}")

        # Create sample trades (last 30 days)
        logger.info("\n3. Creating sample trades...")
        trade_count = 0
        today = date.today()

        # Generate trades for each insider
        for insider in insiders_list:
            company = companies_map.get(insider.company.ticker)
            if not company:
                continue

            # Create 2-5 trades per insider
            num_trades = 3
            for i in range(num_trades):
                try:
                    # Random date in last 30 days
                    days_ago = (i + 1) * 7  # 7, 14, 21 days ago
                    transaction_date = today - timedelta(days=days_ago)
                    filing_date = transaction_date + timedelta(days=2)  # Filed 2 days later

                    # Alternate between BUY and SELL
                    transaction_type = "BUY" if i % 2 == 0 else "SELL"
                    transaction_code = "P" if transaction_type == "BUY" else "S"

                    # Sample trade data (realistic values)
                    shares = Decimal(1000 + (i * 500))  # 1000, 1500, 2000, etc.
                    price_per_share = Decimal(150 + (i * 10))  # Varying prices
                    total_value = shares * price_per_share

                    # Check for duplicates before creating
                    is_duplicate = await TradeService.check_duplicate(
                        db=db,
                        insider_id=insider.id,
                        transaction_date=transaction_date,
                        shares=shares,
                        price_per_share=price_per_share
                    )

                    if is_duplicate:
                        logger.info(f"   ⊘ Skipped duplicate trade for {insider.name}")
                        continue

                    # Create trade
                    trade_data = TradeCreate(
                        insider_id=insider.id,
                        company_id=company.id,
                        transaction_date=transaction_date,
                        filing_date=filing_date,
                        transaction_type=transaction_type,
                        transaction_code=transaction_code,
                        shares=shares,
                        price_per_share=price_per_share,
                        total_value=total_value,
                        shares_owned_after=Decimal(10000 + (i * 1000)),
                        ownership_type="Direct",
                        derivative_transaction=False,
                        sec_filing_url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={company.cik}&type=4",
                        form_type="Form 4"
                    )

                    trade = await TradeService.create(db=db, trade_data=trade_data)
                    trade_count += 1

                    logger.info(
                        f"   ✓ Created trade: {company.ticker} | {insider.name} | "
                        f"{transaction_type} {shares} shares @ ${price_per_share}"
                    )

                except Exception as e:
                    logger.error(f"   ✗ Error creating trade for {insider.name}: {e}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Database seeding complete!")
    logger.info(f"✓ Companies: {len(companies_map)}")
    logger.info(f"✓ Insiders: {len(insiders_list)}")
    logger.info(f"✓ Trades: {trade_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    """Run seeding script."""

    # ⚠️ PRODUCTION SAFETY CHECK
    if settings.is_production:
        logger.error("=" * 80)
        logger.error("❌ BLOCKED: Cannot run seed_data.py in PRODUCTION environment!")
        logger.error("=" * 80)
        logger.error("This script creates dummy/test data and should NEVER be run in production.")
        logger.error("Current environment: %s", settings.environment)
        logger.error("To run this script, set ENVIRONMENT=development in your .env file")
        logger.error("=" * 80)
        sys.exit(1)

    # ⚠️ CONFIRMATION PROMPT
    logger.warning("=" * 80)
    logger.warning("⚠️  WARNING: This will create DUMMY DATA in your database!")
    logger.warning("=" * 80)
    logger.warning("Environment: %s", settings.environment)
    logger.warning("Database: %s", settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url)
    logger.warning("")
    logger.warning("This script will create:")
    logger.warning("  - Sample companies (AAPL, TSLA, MSFT, NVDA, GOOGL)")
    logger.warning("  - Sample insiders with fictional data")
    logger.warning("  - Sample trades with programmatically generated values")
    logger.warning("")

    response = input("Type 'yes' to continue or 'no' to cancel: ").strip().lower()

    if response != 'yes':
        logger.info("Seeding cancelled by user.")
        sys.exit(0)

    logger.info("Starting database seeding...")
    asyncio.run(seed_database())
