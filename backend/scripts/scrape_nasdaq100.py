"""
Script to scrape all NASDAQ 100 companies from SEC EDGAR.

⚠️ WARNING: This will make many requests to SEC EDGAR API.
SEC rate limit: 10 requests/second
This script respects rate limiting with delays between requests.
"""

import asyncio
import platform
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_manager
from app.services.scraper_service import ScraperService

# NASDAQ 100 companies (as of 2024)
# This list includes major companies from NASDAQ 100 index
NASDAQ_100 = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "TSLA", "META", "AVGO", "COST",
    "NFLX", "AMD", "PEP", "ADBE", "CSCO", "TXN", "CMCSA", "QCOM", "AMGN", "INTU",
    "INTC", "AMAT", "ISRG", "REGN", "BKNG", "ADI", "VRSK", "SNPS", "CDNS", "ASML",
    "CRWD", "FANG", "MU", "FTNT", "NXPI", "MELI", "ADSK", "CTSH", "LRCX", "ODFL",
    "PAYX", "KLAC", "BKR", "ON", "DXCM", "IDXX", "FAST", "GEHC", "TEAM", "ANSS",
    "ZS", "CDW", "PCAR", "MCHP", "ROST", "TTWO", "EXC", "ALGN", "WBD", "EBAY",
    "CSGP", "CTAS", "KDP", "NDAQ", "VRSN", "AEP", "ENPH", "BIIB", "MRVL", "CPRT",
    "GFS", "DLTR", "SGEN", "NTES", "XEL", "NXPI", "FTNT", "ZS", "CDNS", "VRSK",
    "ON", "DXCM", "IDXX", "FAST", "GEHC", "TEAM", "ANSS", "CDW", "PCAR", "ROST",
    "TTWO", "ALGN", "WBD", "EBAY", "CSGP", "CTAS", "KDP", "NDAQ", "AEP", "BIIB",
    "MRVL", "CPRT", "GFS", "DLTR", "SGEN", "NTES", "XEL", "FAST", "GEHC", "TEAM"
]

# Remove duplicates while preserving order
NASDAQ_100 = sorted(list(dict.fromkeys(NASDAQ_100)))

# Fix for Windows async event loop
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def scrape_all_companies():
    """Scrape all NASDAQ 100 companies."""
    print("=" * 80)
    print(f"Starting NASDAQ 100 scrape for {len(NASDAQ_100)} companies")
    print("=" * 80)
    print(f"SEC rate limit: 10 requests/second")
    print(f"Estimated time: ~{len(NASDAQ_100) * 2 / 60:.1f} minutes")
    print("=" * 80)
    print()

    scraper = ScraperService()
    results = {
        "success": [],
        "failed": [],
        "total_filings": 0,
        "total_trades": 0
    }

    async with db_manager.get_session() as db:
        for i, ticker in enumerate(NASDAQ_100, 1):
            print(f"[{i}/{len(NASDAQ_100)}] Scraping {ticker}...", end=" ", flush=True)
            
            try:
                result = await scraper.scrape_company_trades(
                    db=db,
                    ticker=ticker,
                    days_back=90,  # Last 90 days
                    max_filings=10  # Max 10 filings per company
                )
                
                if result["success"]:
                    filings = result.get("filings_processed", 0)
                    trades = result.get("trades_created", 0)
                    results["success"].append(ticker)
                    results["total_filings"] += filings
                    results["total_trades"] += trades
                    print(f"OK: {filings} filings, {trades} trades")
                else:
                    results["failed"].append(ticker)
                    print(f"FAILED: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                results["failed"].append(ticker)
                print(f"ERROR: {str(e)[:50]}")
            
            # Rate limiting: SEC allows 10 req/sec, so wait 0.11 seconds between requests
            # (slightly more than 1/10 to be safe)
            if i < len(NASDAQ_100):
                await asyncio.sleep(0.12)
            
            # Commit after each company
            await db.commit()

    print()
    print("=" * 80)
    print("Scraping complete!")
    print("=" * 80)
    print(f"Successful: {len(results['success'])} companies")
    print(f"Failed: {len(results['failed'])} companies")
    print(f"Total filings processed: {results['total_filings']}")
    print(f"Total trades created: {results['total_trades']}")
    print("=" * 80)
    
    if results["failed"]:
        print("\nFailed companies:")
        for ticker in results["failed"]:
            print(f"  - {ticker}")
    
    return results


if __name__ == "__main__":
    print("\nWARNING: This will scrape data for 100 companies from SEC EDGAR")
    print("This may take 15-30 minutes due to rate limiting.\n")
    
    response = input("Type 'yes' to continue or 'no' to cancel: ").strip().lower()
    
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    asyncio.run(scrape_all_companies())

