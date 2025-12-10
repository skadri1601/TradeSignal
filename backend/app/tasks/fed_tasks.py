from app.core.celery_app import celery_app
import logging
from app.config import settings
from app.core.redis_cache import get_cache
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class FredAPIClient:
    """
    Helper class to fetch data from FRED API within Celery tasks,
    handling its own rate limiting and caching.
    """
    def __init__(self):
        self.fred_api_key = getattr(settings, "FRED_API_KEY", None)
        self.base_url = "https://api.stlouisfed.org/fred"
        self.redis = get_cache()
        self.rate_limit = 120  # FRED free tier: 120 calls/minute
        self._request_times: List[float] = []
        self._lock = asyncio.Lock() # Use asyncio.Lock for async methods

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
                        f"FRED API rate limit reached. Waiting {wait_time:.2f} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                    # Clean up old requests after waiting
                    now = asyncio.get_event_loop().time()
                    self._request_times = [
                        t for t in self._request_times if now - t < 60
                    ]
            # Record this request
            self._request_times.append(now)

    async def _fetch_and_cache_fred_series(self, series_id: str, cache_key: str, cache_ttl: int,
                                           params: Optional[Dict[str, Any]] = None,
                                           post_process_func: Optional[Any] = None) -> None:
        """
        Generic method to fetch FRED series data and save to cache.
        """
        if not self.fred_api_key:
            logger.warning(f"FRED API key not configured for series {series_id}.")
            return

        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/series/observations"
                default_params = {
                    "series_id": series_id,
                    "api_key": self.fred_api_key,
                    "file_type": "json",
                }
                if params:
                    default_params.update(params)
                
                response = await client.get(url, params=default_params)
                response.raise_for_status()
                data = response.json()

                result = data
                if post_process_func:
                    result = post_process_func(data)

                if self.redis.enabled():
                    self.redis.set(cache_key, result, ttl=cache_ttl)
                    logger.info(f"Successfully fetched and cached FRED series {series_id}.")
                else:
                    logger.warning("Redis is not enabled, FRED data not cached.")

        except httpx.HTTPStatusError as e:
            logger.error(f"FRED API HTTP error for series {series_id}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"FRED API request error for series {series_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching FRED series {series_id}: {e}", exc_info=True)


fred_api_client = FredAPIClient()

def _process_interest_rate(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Helper to process FRED FEDFUNDS data."""
    if "observations" in data and len(data["observations"]) > 0:
        latest = data["observations"][0]
        if latest.get("value") != ".":
            return {
                "rate": float(latest.get("value", 0)),
                "date": latest.get("date"),
                "unit": "percent",
                "description": "Federal Funds Effective Rate",
            }
    return None

def _process_rate_history(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Helper to process FRED FEDFUNDS history data."""
    if "observations" in data:
        return [
            {
                "date": obs.get("date"),
                "rate": float(obs.get("value", 0)),
                "unit": "percent",
            }
            for obs in data["observations"]
            if obs.get("value") != "."
        ]
    return []

def _process_economic_indicators(data: Dict[str, Any], series_id: str) -> Optional[Dict[str, Any]]:
    """Helper to process a single economic indicator from FRED."""
    if "observations" in data and len(data["observations"]) > 0:
        latest = data["observations"][0]
        if latest.get("value") != ".":
            return {
                "value": float(latest.get("value", 0)),
                "date": latest.get("date"),
                "series_id": series_id,
            }
    return None


@celery_app.task(name="fetch_current_interest_rate")
def fetch_current_interest_rate_task():
    """Celery task to fetch and cache current Federal Reserve interest rate."""
    logger.info("Starting fetch_current_interest_rate_task...")
    asyncio.run(fred_api_client._fetch_and_cache_fred_series(
        series_id="FEDFUNDS",
        cache_key="fed:interest-rate",
        cache_ttl=3600, # 1 hour
        params={"sort_order": "desc", "limit": 1},
        post_process_func=_process_interest_rate
    ))

@celery_app.task(name="fetch_rate_history")
def fetch_rate_history_task(days_back: int = 365):
    """Celery task to fetch and cache interest rate history."""
    logger.info(f"Starting fetch_rate_history_task for {days_back} days back...")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    asyncio.run(fred_api_client._fetch_and_cache_fred_series(
        series_id="FEDFUNDS",
        cache_key=f"fed:rate-history:{days_back}",
        cache_ttl=21600, # 6 hours
        params={"observation_start": start_date, "sort_order": "desc"},
        post_process_func=_process_rate_history
    ))

@celery_app.task(name="fetch_economic_indicator")
def fetch_economic_indicator_task(indicator_name: str, series_id: str):
    """Celery task to fetch and cache a single economic indicator."""
    logger.info(f"Starting fetch_economic_indicator_task for {indicator_name} ({series_id})...")
    async def _fetch():
        await fred_api_client._fetch_and_cache_fred_series(
            series_id=series_id,
            cache_key=f"fed:indicator:{indicator_name}",
            cache_ttl=3600, # 1 hour
            params={"sort_order": "desc", "limit": 1},
            post_process_func=lambda data: _process_economic_indicators(data, series_id)
        )
    asyncio.run(_fetch())
