"""
Render Cron Job Script - Scrapes SEC EDGAR, Congressional trades, and Market News.

This script is designed to be run by Render's cron job scheduler.
No user interaction required.

Usage:
    python scripts/cron_scrape.py [--type TYPE] [--days DAYS]

Options:
    --type    Type of scrape: 'all', 'insider', 'congressional', 'news' (default: all)
    --days    Days to look back (default: 30 for insider, 60 for congressional)

Render Cron Setup:
    1. Go to Render Dashboard > Your Service > Cron Jobs
    2. Add new cron job with command: cd backend && python scripts/cron_scrape.py
    3. Set schedule (e.g., "0 */6 * * *" for every 6 hours)
"""

import asyncio
import argparse
import platform
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix for Windows async event loop
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def scrape_insider_trades(days_back: int = 30, max_filings: int = 50):
    """Scrape insider trades from SEC EDGAR for all watchlist companies."""
    from app.database import db_manager
    from app.services.scraper_service import ScraperService
    from app.models import Company
    from sqlalchemy import select
    import os

    logger.info("=" * 80)
    logger.info("Starting Insider Trades Scrape")
    logger.info(f"Days back: {days_back}, Max filings per company: {max_filings}")
    logger.info("=" * 80)

    # Load companies from watchlist file
    watchlist_path = Path(__file__).parent.parent / "app" / "watchlist_companies.txt"
    tickers = []

    try:
        with open(watchlist_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    tickers.append(line)
        logger.info(f"Loaded {len(tickers)} companies from watchlist")
    except FileNotFoundError:
        logger.warning("Watchlist file not found, loading from database...")
        async with db_manager.get_session() as db:
            result = await db.execute(select(Company))
            companies = result.scalars().all()
            tickers = [c.ticker for c in companies if c.ticker]
            logger.info(f"Loaded {len(tickers)} companies from database")

    if not tickers:
        logger.error("No companies found to scrape!")
        return {"success": False, "error": "No companies found"}

    scraper = ScraperService()
    results = {
        "success": [],
        "failed": [],
        "total_filings": 0,
        "total_trades": 0
    }

    async with db_manager.get_session() as db:
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"[{i}/{len(tickers)}] Scraping {ticker}...")

            try:
                result = await scraper.scrape_company_trades(
                    db=db,
                    ticker=ticker,
                    days_back=days_back,
                    max_filings=max_filings
                )

                if result.get("success"):
                    filings = result.get("filings_processed", 0)
                    trades = result.get("trades_created", 0)
                    results["success"].append(ticker)
                    results["total_filings"] += filings
                    results["total_trades"] += trades
                    logger.info(f"  OK: {filings} filings, {trades} trades")
                else:
                    results["failed"].append(ticker)
                    logger.warning(f"  FAILED: {result.get('message', 'Unknown')}")

            except Exception as e:
                results["failed"].append(ticker)
                logger.error(f"  ERROR: {str(e)[:100]}")

            # Rate limiting for SEC (10 req/sec limit)
            await asyncio.sleep(0.12)
            await db.commit()

    logger.info("=" * 80)
    logger.info("Insider Trades Scrape Complete")
    logger.info(f"Successful: {len(results['success'])}, Failed: {len(results['failed'])}")
    logger.info(f"Total filings: {results['total_filings']}, Total trades: {results['total_trades']}")
    logger.info("=" * 80)

    return results


async def scrape_congressional_trades(days_back: int = 60):
    """Scrape congressional trades from data sources."""
    from app.database import db_manager
    from app.services.congressional_scraper import CongressionalScraperService

    logger.info("=" * 80)
    logger.info("Starting Congressional Trades Scrape")
    logger.info(f"Days back: {days_back}")
    logger.info("=" * 80)

    scraper = CongressionalScraperService()

    async with db_manager.get_session() as db:
        try:
            result = await scraper.scrape_congressional_trades(
                db=db,
                days_back=days_back
            )

            trades_created = result.get("trades_created", 0)
            trades_processed = result.get("trades_processed", 0)

            logger.info("=" * 80)
            logger.info("Congressional Trades Scrape Complete")
            logger.info(f"Trades processed: {trades_processed}, Trades created: {trades_created}")
            logger.info("=" * 80)

            return {"success": True, **result}

        except Exception as e:
            logger.error(f"Congressional scrape failed: {e}")
            return {"success": False, "error": str(e)}


async def fetch_market_news():
    """Fetch market news from Finnhub and cache in Redis."""
    import httpx
    from app.config import settings
    from app.core.redis_cache import get_cache
    from datetime import timedelta

    logger.info("=" * 80)
    logger.info("Starting Market News Fetch")
    logger.info("=" * 80)

    finnhub_api_key = getattr(settings, "finnhub_api_key", None)
    if not finnhub_api_key:
        logger.error("Finnhub API key not configured!")
        return {"success": False, "error": "No API key"}

    redis = get_cache()
    if not redis or not redis.enabled():
        logger.error("Redis not available - news cannot be cached!")
        return {"success": False, "error": "Redis not available"}

    base_url = "https://finnhub.io/api/v1"
    cache_ttl = 21600  # 6 hours
    results = {"general": 0, "crypto": 0}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Fetch general market news
        try:
            response = await client.get(
                f"{base_url}/news",
                params={"category": "general", "token": finnhub_api_key}
            )
            response.raise_for_status()
            data = response.json()

            # Filter to last 7 days
            cutoff = int((datetime.now() - timedelta(days=7)).timestamp())
            filtered = [a for a in data if a.get("datetime", 0) >= cutoff]
            filtered.sort(key=lambda x: x.get("datetime", 0), reverse=True)

            redis.set("news:general", filtered, ttl=cache_ttl)
            results["general"] = len(filtered)
            logger.info(f"Cached {len(filtered)} general news articles")
        except Exception as e:
            logger.error(f"Failed to fetch general news: {e}")

        await asyncio.sleep(0.5)  # Rate limiting

        # Fetch crypto news
        try:
            response = await client.get(
                f"{base_url}/news",
                params={"category": "crypto", "token": finnhub_api_key}
            )
            response.raise_for_status()
            data = response.json()

            cutoff = int((datetime.now() - timedelta(days=7)).timestamp())
            filtered = [a for a in data if a.get("datetime", 0) >= cutoff]
            filtered.sort(key=lambda x: x.get("datetime", 0), reverse=True)

            redis.set("news:crypto", filtered, ttl=cache_ttl)
            results["crypto"] = len(filtered)
            logger.info(f"Cached {len(filtered)} crypto news articles")
        except Exception as e:
            logger.error(f"Failed to fetch crypto news: {e}")

    logger.info("=" * 80)
    logger.info("Market News Fetch Complete")
    logger.info(f"General: {results['general']}, Crypto: {results['crypto']}")
    logger.info("=" * 80)

    return {"success": True, **results}


async def main(scrape_type: str, days: int = None):
    """Main entry point for cron job."""
    start_time = datetime.now()
    logger.info(f"Cron scrape started at {start_time.isoformat()}")
    logger.info(f"Scrape type: {scrape_type}")

    results = {}

    if scrape_type in ("all", "insider"):
        insider_days = days or 30
        results["insider"] = await scrape_insider_trades(days_back=insider_days)

    if scrape_type in ("all", "congressional"):
        congressional_days = days or 60
        results["congressional"] = await scrape_congressional_trades(days_back=congressional_days)

    if scrape_type in ("all", "news"):
        results["news"] = await fetch_market_news()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Cron scrape completed in {duration:.1f} seconds")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Cron Job - Scrape trades data")
    parser.add_argument(
        "--type",
        choices=["all", "insider", "congressional", "news"],
        default="all",
        help="Type of scrape to run"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Days to look back (default: 30 for insider, 60 for congressional)"
    )

    args = parser.parse_args()
    asyncio.run(main(args.type, args.days))
