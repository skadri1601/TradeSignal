#!/usr/bin/env python3
"""
Batch scrape all companies from watchlist.
Handles rate limiting and provides progress updates.
"""

import requests
import time
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000/api/v1/scraper/scrape"
MAX_FILINGS = 10
DELAY_BETWEEN_REQUESTS = 2  # seconds to respect SEC rate limits
BATCH_SIZE = 10  # How many to scrape before a longer pause

def load_tickers():
    """Load ticker symbols from watchlist file."""
    watchlist_file = Path(__file__).parent / "backend" / "watchlist_companies.txt"
    tickers = []

    with open(watchlist_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                tickers.append(line)

    return tickers

def scrape_ticker(ticker):
    """Scrape a single ticker."""
    try:
        url = f"{API_URL}/{ticker}"
        params = {"max_filings": MAX_FILINGS}

        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()

        data = response.json()
        return {
            "ticker": ticker,
            "success": data.get("success", False),
            "filings": data.get("filings_processed", 0),
            "trades": data.get("trades_created", 0),
            "error": data.get("errors")
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "success": False,
            "filings": 0,
            "trades": 0,
            "error": str(e)
        }

def main():
    """Main scraping orchestrator."""
    tickers = load_tickers()
    total_tickers = len(tickers)

    print(f"Starting batch scrape of {total_tickers} companies...")
    print(f"Estimated time: {total_tickers * DELAY_BETWEEN_REQUESTS / 60:.1f} minutes\n")

    results = {
        "successful": 0,
        "failed": 0,
        "total_filings": 0,
        "total_trades": 0,
        "errors": []
    }

    start_time = time.time()

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{total_tickers}] Scraping {ticker}...", end=" ")

        result = scrape_ticker(ticker)

        if result["success"]:
            results["successful"] += 1
            results["total_filings"] += result["filings"]
            results["total_trades"] += result["trades"]
            print(f"OK - {result['filings']} filings, {result['trades']} trades")
        else:
            results["failed"] += 1
            results["errors"].append(f"{ticker}: {result['error']}")
            print(f"FAILED - {result['error']}")

        # Progress update every 20 companies
        if i % 20 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total_tickers - i) / rate if rate > 0 else 0
            print(f"\nProgress: {i}/{total_tickers} ({i/total_tickers*100:.1f}%)")
            print(f"   Successful: {results['successful']}, Failed: {results['failed']}")
            print(f"   Trades created: {results['total_trades']}")
            print(f"   ETA: {remaining/60:.1f} minutes\n")

        # Delay between requests to respect rate limits
        if i < total_tickers:
            time.sleep(DELAY_BETWEEN_REQUESTS)

            # Longer pause every batch
            if i % BATCH_SIZE == 0:
                print(f"   Pausing 5 seconds to respect SEC rate limits...")
                time.sleep(5)

    # Final summary
    elapsed_total = time.time() - start_time
    print("\n" + "="*60)
    print("SCRAPING COMPLETE!")
    print("="*60)
    print(f"Successful: {results['successful']}/{total_tickers}")
    print(f"Failed: {results['failed']}/{total_tickers}")
    print(f"Total filings processed: {results['total_filings']}")
    print(f"Total trades created: {results['total_trades']}")
    print(f"Total time: {elapsed_total/60:.1f} minutes")
    print(f"Average rate: {total_tickers/elapsed_total*60:.1f} companies/minute")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results["errors"][:10]:  # Show first 10 errors
            print(f"   - {error}")
        if len(results["errors"]) > 10:
            print(f"   ... and {len(results['errors']) - 10} more")

    print("\nDatabase is now populated with insider trading data!")
    print("You can now explore AI insights with full dataset")

if __name__ == "__main__":
    main()
