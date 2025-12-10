from app.core.celery_app import celery_app
import logging
from app.config import settings
from app.core.redis_cache import get_cache
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# Re-implementing the rate-limiting and parsing logic for the Celery tasks
class FinnhubNewsFetcher:
    """
    Helper class to fetch news from Finnhub within Celery tasks,
    handling its own rate limiting and caching.
    """
    def __init__(self):
        self.finnhub_api_key = getattr(settings, "finnhub_api_key", None)
        self.rate_limit = 60  # Finnhub free tier: 60 calls/minute
        self.cache_ttl = 21600  # 6 hours in seconds
        self.base_url = "https://finnhub.io/api/v1"
        self.redis = get_cache()
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
                        f"Rate limit reached. Waiting {wait_time:.2f} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                    # Clean up old requests after waiting
                    now = asyncio.get_event_loop().time()
                    self._request_times = [
                        t for t in self._request_times if now - t < 60
                    ]
            # Record this request
            self._request_times.append(now)

    def _filter_recent_news(
        self, news_data: List[Dict[str, Any]], days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Filter news articles to only include those from the last N days.
        """
        if not isinstance(news_data, list):
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = int(cutoff_date.timestamp())

        filtered = []
        for article in news_data:
            article_datetime = article.get("datetime", 0)
            if article_datetime >= cutoff_timestamp:
                filtered.append(article)

        filtered.sort(key=lambda x: x.get("datetime", 0), reverse=True)
        return filtered

    async def _fetch_and_cache_news(self, category: str, ticker: Optional[str] = None) -> None:
        """
        Generic method to fetch news from Finnhub and save to cache.
        """
        if not self.finnhub_api_key:
            logger.warning(f"Finnhub API key not configured for {category} news.")
            return

        cache_key = f"news:{category}:{ticker}" if ticker else f"news:{category}"

        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/news"
                params = {"category": category, "token": self.finnhub_api_key}
                if ticker and category == "company":
                    url = f"{self.base_url}/company-news"
                    params["symbol"] = ticker.upper()
                    to_date = datetime.now()
                    from_date = to_date - timedelta(days=7)
                    params["from"] = from_date.strftime("%Y-%m-%d")
                    params["to"] = to_date.strftime("%Y-%m-%d")
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                filtered_news = self._filter_recent_news(data, days=7)

                if self.redis.enabled():
                    self.redis.set(cache_key, filtered_news, ttl=self.cache_ttl)
                    logger.info(f"Successfully fetched and cached {len(filtered_news)} {category} news articles (ticker: {ticker or 'N/A'}).")
                else:
                    logger.warning("Redis is not enabled, news not cached.")

        except httpx.HTTPStatusError as e:
            logger.error(f"Finnhub HTTP error for {category} news (ticker: {ticker or 'N/A'}): {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Finnhub request error for {category} news (ticker: {ticker or 'N/A'}): {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching Finnhub {category} news (ticker: {ticker or 'N/A'}): {e}", exc_info=True)


finnhub_news_fetcher = FinnhubNewsFetcher()

@celery_app.task(name="fetch_general_news")
def fetch_general_news_task():
    """Celery task to fetch and cache general market news."""
    logger.info("Starting fetch_general_news_task...")
    asyncio.run(finnhub_news_fetcher._fetch_and_cache_news("general"))

@celery_app.task(name="fetch_crypto_news")
def fetch_crypto_news_task():
    """Celery task to fetch and cache crypto news."""
    logger.info("Starting fetch_crypto_news_task...")
    asyncio.run(finnhub_news_fetcher._fetch_and_cache_news("crypto"))

@celery_app.task(name="fetch_company_news")
def fetch_company_news_task(ticker: str):
    """Celery task to fetch and cache company-specific news."""
    logger.info(f"Starting fetch_company_news_task for ticker: {ticker}...")
    asyncio.run(finnhub_news_fetcher._fetch_and_cache_news("company", ticker))

