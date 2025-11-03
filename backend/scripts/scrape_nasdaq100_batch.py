"""
Batch script to scrape NASDAQ 100 companies using the API endpoint.
This version uses HTTP requests so you can see progress.
"""

import requests
import time
import json

# NASDAQ 100 companies (unique list)
NASDAQ_100 = [
    "MSFT", "NVDA", "TSLA", "META", "NFLX", "PEP", "TXN", "QCOM", "INTU", "INTC",
    "ISRG", "REGN", "VRSK", "SNPS", "MU", "NXPI", "MELI", "LRCX", "ODFL", "PAYX",
    "KLAC", "ON", "TEAM", "ZS", "PCAR", "MCHP", "ROST", "TTWO", "WBD", "KDP",
    "NDAQ", "VRSN", "MRVL", "SGEN", "NTES", "XEL", "TTD", "LCID", "MNDY", "OKTA",
    "ROKU", "SWKS", "SPLK", "ZM", "RIVN", "NBIX"
]

# Remove duplicates
NASDAQ_100 = sorted(list(dict.fromkeys(NASDAQ_100)))

API_BASE = "http://localhost:8000/api/v1/scraper/scrape"

def scrape_all():
    """Scrape all companies using API."""
    print("=" * 80)
    print(f"Starting NASDAQ 100 scrape for {len(NASDAQ_100)} companies")
    print("=" * 80)
    print(f"SEC rate limit: 10 requests/second")
    print(f"Estimated time: ~{len(NASDAQ_100) * 2 / 60:.1f} minutes")
    print("=" * 80)
    print()
    
    results = {
        "success": [],
        "failed": [],
        "total_filings": 0,
        "total_trades": 0
    }
    
    for i, ticker in enumerate(NASDAQ_100, 1):
        print(f"[{i}/{len(NASDAQ_100)}] Scraping {ticker}...", end=" ", flush=True)
        
        try:
            url = f"{API_BASE}/{ticker}?days_back=90&max_filings=10"
            response = requests.get(url, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    filings = data.get("filings_processed", 0)
                    trades = data.get("trades_created", 0)
                    results["success"].append(ticker)
                    results["total_filings"] += filings
                    results["total_trades"] += trades
                    print(f"OK: {filings} filings, {trades} trades")
                else:
                    results["failed"].append(ticker)
                    print(f"FAILED: {data.get('message', 'Unknown error')}")
            else:
                results["failed"].append(ticker)
                print(f"HTTP {response.status_code}")
                
        except Exception as e:
            results["failed"].append(ticker)
            print(f"ERROR: {str(e)[:50]}")
        
        # Rate limiting: wait 0.12 seconds between requests
        if i < len(NASDAQ_100):
            time.sleep(0.12)
    
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

if __name__ == "__main__":
    scrape_all()

