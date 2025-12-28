"""
Finnhub Data Service

Fetches market data from Finnhub API.
Rate limit: 60 calls/minute (free tier).
Uses Supabase caching to stay within limits.
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
import asyncio

import httpx
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.company import Company
from app.models.market_data import PriceTarget, EarningsSurprise
from app.services.supabase_cache_service import supabase_cache_service

logger = logging.getLogger(__name__)


class FinnhubService:
    """
    Service for fetching data from Finnhub API.

    Rate limited to 60 calls/min. Uses caching aggressively.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    # Cache TTLs in minutes
    PRICE_TARGET_TTL = 360  # 6 hours
    EARNINGS_SURPRISE_TTL = 360  # 6 hours
    IPO_CALENDAR_TTL = 60  # 1 hour
    ECONOMIC_CALENDAR_TTL = 60  # 1 hour

    def __init__(self):
        self.api_key = settings.finnhub_api_key
        if not self.api_key:
            logger.warning("Finnhub API key not configured")
        self.rate_limit = 60  # Finnhub free tier: 60 calls/minute
        self._request_times: List[float] = []
        self._lock = asyncio.Lock()

    async def _rate_limit(self) -> None:
        """Implement rate limiting (token bucket algorithm)."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            # Remove requests older than 1 minute
            self._request_times = [t for t in self._request_times if now - t < 60]

            # Check if we've hit the rate limit
            if len(self._request_times) >= self.rate_limit:
                # Calculate wait time
                oldest_request = self._request_times[0]
                wait_time = 60 - (now - oldest_request)
                if wait_time > 0:
                    logger.warning(
                        f"Finnhub rate limit reached. Waiting {wait_time:.2f} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                    # Clean up old requests after waiting
                    now = asyncio.get_event_loop().time()
                    self._request_times = [
                        t for t in self._request_times if now - t < 60
                    ]
            # Record this request
            self._request_times.append(now)

    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to Finnhub API with rate limiting awareness."""
        if not self.api_key:
            return None

        await self._rate_limit()

        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["token"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 429:
                    logger.warning("Finnhub rate limit hit")
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Finnhub API error: {e}", exc_info=True)
            return None

    async def get_price_target(
        self,
        db: AsyncSession,
        ticker: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get analyst price targets for a stock.

        Returns:
            Dict with target_high, target_low, target_mean, target_median
        """
        cache_key = f"finnhub:price_target:{ticker}"

        # Check cache first
        if not force_refresh:
            cached = await supabase_cache_service.get(cache_key)
            if cached:
                return cached

        # Fetch from API
        data = await self._make_request("stock/price-target", {"symbol": ticker})

        if not data:
            return None

        result = {
            "target_high": data.get("targetHigh"),
            "target_low": data.get("targetLow"),
            "target_mean": data.get("targetMean"),
            "target_median": data.get("targetMedian"),
            "last_updated": data.get("lastUpdated"),
        }

        # Cache it
        await supabase_cache_service.set(
            cache_key, result,
            ttl_minutes=self.PRICE_TARGET_TTL,
            cache_type="finnhub"
        )

        # Also save to database for persistence
        await self._save_price_target(db, ticker, result)

        return result

    async def get_earnings_surprises(
        self,
        db: AsyncSession,
        ticker: str,
        limit: int = 4,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get historical earnings surprises (actual vs estimate).

        Returns:
            List of earnings with actual, estimate, surprise, surprisePercent
        """
        cache_key = f"finnhub:earnings_surprise:{ticker}"

        if not force_refresh:
            cached = await supabase_cache_service.get(cache_key)
            if cached:
                return cached[:limit] if isinstance(cached, list) else []

        data = await self._make_request("stock/earnings", {"symbol": ticker})

        if not data or not isinstance(data, list):
            return []

        results = []
        for item in data[:limit]:
            results.append({
                "period": item.get("period"),
                "actual": item.get("actual"),
                "estimate": item.get("estimate"),
                "surprise": item.get("surprise"),
                "surprise_percent": item.get("surprisePercent"),
            })

        # Cache it
        await supabase_cache_service.set(
            cache_key, results,
            ttl_minutes=self.EARNINGS_SURPRISE_TTL,
            cache_type="finnhub"
        )

        # Save to database
        await self._save_earnings_surprises(db, ticker, results)

        return results

    async def get_ipo_calendar(
        self,
        from_date: date = None,
        to_date: date = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get IPO calendar (global, not per-stock).

        Returns:
            List of upcoming IPOs
        """
        if not from_date:
            from_date = date.today()
        if not to_date:
            to_date = from_date + timedelta(days=30)

        cache_key = f"finnhub:ipo_calendar:{from_date}:{to_date}"

        if not force_refresh:
            cached = await supabase_cache_service.get(cache_key)
            if cached:
                return cached if isinstance(cached, list) else []

        data = await self._make_request("calendar/ipo", {
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        })

        if not data or "ipoCalendar" not in data:
            return []

        results = []
        for item in data["ipoCalendar"]:
            results.append({
                "symbol": item.get("symbol"),
                "company_name": item.get("name"),
                "exchange": item.get("exchange"),
                "ipo_date": item.get("date"),
                "price_range": f"${item.get('priceRangeLow', 'N/A')} - ${item.get('priceRangeHigh', 'N/A')}",
                "shares": item.get("numberOfShares"),
                "status": item.get("status"),
            })

        await supabase_cache_service.set(
            cache_key, results,
            ttl_minutes=self.IPO_CALENDAR_TTL,
            cache_type="finnhub"
        )

        return results

    async def get_economic_calendar(
        self,
        from_date: date = None,
        to_date: date = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get economic calendar (Fed meetings, CPI, jobs, etc.).

        Returns:
            List of economic events
        """
        if not from_date:
            from_date = date.today()
        if not to_date:
            to_date = from_date + timedelta(days=14)

        cache_key = f"finnhub:economic_calendar:{from_date}:{to_date}"

        if not force_refresh:
            cached = await supabase_cache_service.get(cache_key)
            if cached:
                return cached if isinstance(cached, list) else []

        data = await self._make_request("calendar/economic", {
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        })

        if not data or "economicCalendar" not in data:
            return []

        results = []
        for item in data["economicCalendar"]:
            event_time = item.get("time", "")
            results.append({
                "event": item.get("event"),
                "country": item.get("country"),
                "date": event_time[:10] if event_time and len(event_time) >= 10 else None,
                "time": event_time[11:16] if event_time and len(event_time) > 10 else None,
                "impact": item.get("impact"),
                "actual": item.get("actual"),
                "estimate": item.get("estimate"),
                "previous": item.get("prev"),
                "unit": item.get("unit"),
            })

        await supabase_cache_service.set(
            cache_key, results,
            ttl_minutes=self.ECONOMIC_CALENDAR_TTL,
            cache_type="finnhub"
        )

        return results

    # Database persistence helpers

    async def _save_price_target(
        self, db: AsyncSession, ticker: str, data: Dict
    ) -> None:
        """Save price target to database."""
        company = await self._get_company(db, ticker)
        if not company:
            return

        result = await db.execute(
            select(PriceTarget).where(PriceTarget.company_id == company.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.target_high = Decimal(str(data.get("target_high"))) if data.get("target_high") else None
            existing.target_low = Decimal(str(data.get("target_low"))) if data.get("target_low") else None
            existing.target_mean = Decimal(str(data.get("target_mean"))) if data.get("target_mean") else None
            existing.target_median = Decimal(str(data.get("target_median"))) if data.get("target_median") else None
            existing.last_updated = date.today()
            existing.updated_at = datetime.utcnow()
        else:
            pt = PriceTarget(
                company_id=company.id,
                target_high=Decimal(str(data.get("target_high"))) if data.get("target_high") else None,
                target_low=Decimal(str(data.get("target_low"))) if data.get("target_low") else None,
                target_mean=Decimal(str(data.get("target_mean"))) if data.get("target_mean") else None,
                target_median=Decimal(str(data.get("target_median"))) if data.get("target_median") else None,
                last_updated=date.today(),
            )
            db.add(pt)

        await db.commit()

    async def _save_earnings_surprises(
        self, db: AsyncSession, ticker: str, data: List[Dict]
    ) -> None:
        """Save earnings surprises to database."""
        company = await self._get_company(db, ticker)
        if not company:
            return

        # Clear old data
        await db.execute(
            delete(EarningsSurprise).where(EarningsSurprise.company_id == company.id)
        )

        for item in data:
            if not item.get("period"):
                continue

            try:
                period = datetime.strptime(item["period"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue

            actual_eps = item.get("actual", 0) or 0
            estimate_eps = item.get("estimate", 0) or 0
            surprise = item.get("surprise", 0) or 0
            surprise_percent = item.get("surprise_percent", 0) or 0

            es = EarningsSurprise(
                company_id=company.id,
                period=period,
                actual_eps=Decimal(str(actual_eps)),
                estimate_eps=Decimal(str(estimate_eps)),
                surprise=Decimal(str(surprise)),
                surprise_percent=Decimal(str(surprise_percent)),
            )
            db.add(es)

        await db.commit()

    async def _get_company(self, db: AsyncSession, ticker: str) -> Optional[Company]:
        """Get company by ticker."""
        result = await db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()

