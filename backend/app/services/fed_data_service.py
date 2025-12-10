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
from app.config import settings
from app.core.redis_cache import get_cache

logger = logging.getLogger(__name__)


class FedDataService:
    """
    Service for fetching and managing Federal Reserve data.

    This service primarily reads from a Redis cache which is populated by Celery tasks.
    """

    def __init__(self):
        self.redis = get_cache()

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

    async def get_current_interest_rate(self) -> Optional[Dict[str, Any]]:
        """
        Get current Federal Reserve interest rate from cache.
        """
        cache_key = "fed:interest-rate"
        cached = self.redis.get(cache_key)
        if cached:
            return cached
        logger.warning(f"FRED interest rate cache miss for key: {cache_key}")
        return None

    async def get_rate_history(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """
        Get interest rate history from cache.
        """
        cache_key = f"fed:rate-history:{days_back}"
        cached = self.redis.get(cache_key)
        if cached:
            return cached
        logger.warning(f"FRED rate history cache miss for key: {cache_key}")
        return []

    async def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Get key economic indicators from cache.
        """
        cache_key = "fed:indicators"
        cached = self.redis.get(cache_key)
        if cached:
            return cached
        logger.warning(f"FRED economic indicators cache miss for key: {cache_key}")
        return {}

    async def analyze_market_impact(
        self, event_date: datetime, days_before: int = 5, days_after: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze market impact of FED events. (Placeholder)
        """
        return {
            "event_date": event_date.isoformat(),
            "analysis_period": {"before": days_before, "after": days_after},
            "market_impact": "To be calculated with stock price data",
            "sector_impact": "To be calculated",
        }

    async def get_fed_calendar(self, months_ahead: int = 6) -> List[Dict[str, Any]]:
        """
        Get comprehensive FED calendar with meetings and data releases from cache.
        """
        cache_key = f"fed:calendar:{months_ahead}"
        cached = self.redis.get(cache_key)
        if cached:
            return cached
        logger.warning(f"FRED calendar cache miss for key: {cache_key}")

        calendar = []

        # Get FOMC meetings (still relies on local computation)
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
        
        # Sort and cache (this part will be cached by the service itself if needed,
        # or pushed to a dedicated task if the calendar generation is also heavy).
        result = sorted(calendar, key=lambda x: x["date"])
        # For calendar, since it involves local computation of FOMC meetings and other dates,
        # we can still cache it here after computation for faster retrieval on subsequent calls.
        if self.redis.enabled():
            self.redis.set(cache_key, result, ttl=86400) # 24 hours
            logger.info(f"Cached FED calendar data: {cache_key}")
        
        return result

    @staticmethod
    def _get_first_friday(year: int, month: int) -> datetime.date:
        """Get first Friday of a given month."""
        first_day = datetime(year, month, 1)
        days_until_friday = (4 - first_day.weekday()) % 7
        if days_until_friday == 0 and first_day.weekday() != 4:
            days_until_friday = 7
        return (first_day + timedelta(days=days_until_friday)).date()
