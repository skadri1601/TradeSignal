"""
FED Data Service

Fetches and tracks Federal Reserve meetings, rate decisions, and economic data
that affects the stock market.

Data Sources:
- FRED API (Federal Reserve Economic Data)
- FOMC Calendar (Federal Open Market Committee)
- Economic indicators (inflation, employment, GDP)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.redis_cache import get_cache
import httpx
import asyncio

logger = logging.getLogger(__name__)


class FedDataService:
    """
    Service for fetching and managing Federal Reserve data.

    Tracks:
    - FOMC meeting dates
    - Interest rate decisions
    - Economic indicators
    - Market impact analysis
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.fred_api_key = getattr(settings, "FRED_API_KEY", None)
        self.base_url = "https://api.stlouisfed.org/fred"
        self.redis = get_cache()
        self.rate_limit = 120  # FRED free tier: 120 calls/minute
        self._request_times: List[float] = []
        self._lock = asyncio.Lock()

    async def get_upcoming_fomc_meetings(
        self, days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming FOMC meeting dates.

        FOMC typically meets 8 times per year:
        - January, March, May, June, July, September, November, December

        Returns:
            List of upcoming meeting dates with expected outcomes
        """
        # FOMC meeting schedule (approximate, should be fetched from official source)
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        # Typical FOMC schedule (this should be fetched from official calendar)
        meetings = []

        # Generate typical schedule
        current_year = today.year
        typical_months = [1, 3, 5, 6, 7, 9, 11, 12]  # Typical FOMC months

        for month in typical_months:
            # Third Tuesday/Wednesday of month (approximate)
            meeting_date = datetime(current_year, month, 15)
            if meeting_date >= today and meeting_date <= end_date:
                meetings.append(
                    {
                        "date": meeting_date.date().isoformat(),
                        "type": "FOMC Meeting",
                        "description": "Federal Open Market Committee Meeting",
                        "importance": "HIGH",
                        "expected_outcome": "Rate Decision",
                        "days_until": (meeting_date.date() - today.date()).days,
                    }
                )

        return sorted(meetings, key=lambda x: x["date"])

    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieve data from Redis cache."""
        try:
            if self.redis and self.redis.enabled():
                cached_data = self.redis.get(key)
                if cached_data:
                    logger.info(f"Retrieved FRED data from cache: {key}")
                    return cached_data
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        return None

    async def _save_to_cache(self, key: str, value: Any, ttl: int) -> None:
        """Save data to Redis cache."""
        try:
            if self.redis and self.redis.enabled():
                self.redis.set(key, value, ttl=ttl)
                logger.info(f"Cached FRED data: {key}")
        except Exception as e:
            logger.warning(f"Cache save error: {e}")

    async def get_current_interest_rate(self) -> Optional[Dict[str, Any]]:
        """
        Get current Federal Reserve interest rate.

        Uses FRED API series: FEDFUNDS (Federal Funds Effective Rate)
        """
        cache_key = "fed:interest-rate"
        cache_ttl = 3600  # 1 hour

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached

        if not self.fred_api_key:
            logger.warning("FRED API key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/series/observations"
                params = {
                    "series_id": "FEDFUNDS",
                    "api_key": self.fred_api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                }

                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                if "observations" in data and len(data["observations"]) > 0:
                    latest = data["observations"][0]
                    result = {
                        "rate": float(latest.get("value", 0)),
                        "date": latest.get("date"),
                        "unit": "percent",
                        "description": "Federal Funds Effective Rate",
                    }
                    # Cache the result
                    await self._save_to_cache(cache_key, result, cache_ttl)
                    return result
        except Exception as e:
            logger.error(f"Error fetching interest rate from FRED: {e}")
            # Return cached data if available even if API fails
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info("Returning cached interest rate data due to API error")
                return cached
            return None

    async def get_rate_history(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """Get interest rate history."""
        cache_key = f"fed:rate-history:{days_back}"
        cache_ttl = 21600  # 6 hours

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached

        if not self.fred_api_key:
            return []

        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )

            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/series/observations"
                params = {
                    "series_id": "FEDFUNDS",
                    "api_key": self.fred_api_key,
                    "file_type": "json",
                    "observation_start": start_date,
                    "sort_order": "desc",
                }

                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                if "observations" in data:
                    result = [
                        {
                            "date": obs.get("date"),
                            "rate": float(obs.get("value", 0)),
                            "unit": "percent",
                        }
                        for obs in data["observations"]
                        if obs.get("value") != "."
                    ]
                    # Cache the result
                    await self._save_to_cache(cache_key, result, cache_ttl)
                    return result
        except Exception as e:
            logger.error(f"Error fetching rate history: {e}")
            # Return cached data if available even if API fails
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info("Returning cached rate history due to API error")
                return cached
            return []

    async def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Get key economic indicators that affect markets.

        Returns:
            Dict with inflation, employment, GDP data
        """
        cache_key = "fed:indicators"
        cache_ttl = 3600  # 1 hour

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached

        indicators = {}

        if not self.fred_api_key:
            return indicators

        # Key indicators to track
        series_map = {
            "inflation": "CPIAUCSL",  # Consumer Price Index
            "unemployment": "UNRATE",  # Unemployment Rate
            "gdp": "GDP",  # Gross Domestic Product
            "retail_sales": "RSXFS",  # Retail Sales
        }

        try:
            async with httpx.AsyncClient() as client:
                for name, series_id in series_map.items():
                    try:
                        url = f"{self.base_url}/series/observations"
                        params = {
                            "series_id": series_id,
                            "api_key": self.fred_api_key,
                            "file_type": "json",
                            "sort_order": "desc",
                            "limit": 1,
                        }

                        response = await client.get(url, params=params, timeout=10.0)
                        response.raise_for_status()
                        data = response.json()

                        if "observations" in data and len(data["observations"]) > 0:
                            latest = data["observations"][0]
                            indicators[name] = {
                                "value": float(latest.get("value", 0))
                                if latest.get("value") != "."
                                else None,
                                "date": latest.get("date"),
                                "series_id": series_id,
                            }
                    except Exception as e:
                        logger.debug(f"Error fetching {name}: {e}")
                        continue

            # Cache the result
            await self._save_to_cache(cache_key, indicators, cache_ttl)
        except Exception as e:
            logger.error(f"Error fetching economic indicators: {e}")
            # Return cached data if available even if API fails
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info("Returning cached economic indicators due to API error")
                return cached

        return indicators

    async def analyze_market_impact(
        self, event_date: datetime, days_before: int = 5, days_after: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze market impact of FED events.

        Compares market performance before/after FED meetings or rate decisions.
        """
        # This would integrate with stock price data to show impact
        # For now, return structure
        return {
            "event_date": event_date.isoformat(),
            "analysis_period": {"before": days_before, "after": days_after},
            "market_impact": "To be calculated with stock price data",
            "sector_impact": "To be calculated",
        }

    async def get_fed_calendar(self, months_ahead: int = 6) -> List[Dict[str, Any]]:
        """
        Get comprehensive FED calendar with meetings and data releases.

        Returns:
            List of all FED-related events
        """
        cache_key = f"fed:calendar:{months_ahead}"
        cache_ttl = 86400  # 24 hours

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached

        calendar = []

        # Get FOMC meetings
        meetings = await self.get_upcoming_fomc_meetings(days_ahead=months_ahead * 30)
        calendar.extend(meetings)

        # Add economic data release dates (typical schedule)
        # CPI: Monthly, around 10th-15th
        # Employment: First Friday of month
        # GDP: Quarterly, end of month

        today = datetime.now()
        for i in range(months_ahead):
            month = today.month + i
            year = today.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1

            # Employment report (first Friday)
            first_friday = self._get_first_friday(year, month)
            if first_friday >= today.date():
                calendar.append(
                    {
                        "date": first_friday.isoformat(),
                        "type": "Economic Data",
                        "description": "Employment Situation Report (Non-Farm Payrolls)",
                        "importance": "HIGH",
                        "expected_outcome": "Unemployment Rate, Job Growth",
                        "days_until": (first_friday - today.date()).days,
                    }
                )

            # CPI release (typically 10th-15th)
            cpi_date = datetime(year, month, 12).date()
            if cpi_date >= today.date():
                calendar.append(
                    {
                        "date": cpi_date.isoformat(),
                        "type": "Economic Data",
                        "description": "Consumer Price Index (CPI) Release",
                        "importance": "HIGH",
                        "expected_outcome": "Inflation Rate",
                        "days_until": (cpi_date - today.date()).days,
                    }
                )

        result = sorted(calendar, key=lambda x: x["date"])
        # Cache the result
        await self._save_to_cache(cache_key, result, cache_ttl)
        return result

    @staticmethod
    def _get_first_friday(year: int, month: int) -> datetime.date:
        """Get first Friday of a given month."""
        first_day = datetime(year, month, 1)
        days_until_friday = (4 - first_day.weekday()) % 7
        if days_until_friday == 0 and first_day.weekday() != 4:
            days_until_friday = 7
        return (first_day + timedelta(days=days_until_friday)).date()
