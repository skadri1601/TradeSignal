"""
News Service

Fetches and manages market news articles from Finnhub News API.
Implements rate limiting, Redis caching, and error handling.

Data Sources:
- Finnhub News API (general market news, company news, crypto news)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.config import settings
from app.core.redis_cache import get_cache

logger = logging.getLogger(__name__)


class NewsService:
    """
    Service for fetching and managing market news.

    Tracks:
    - General market news
    - Company-specific news
    - Crypto news
    """

    def __init__(self, db: AsyncSession):
        """Initialize the news service."""
        self.db = db
        self.finnhub_api_key = getattr(settings, "finnhub_api_key", None)
        self.rate_limit = 60  # Finnhub free tier: 60 calls/minute
        self.cache_ttl = 21600  # 6 hours in seconds
        self.base_url = "https://finnhub.io/api/v1"
        self.redis = get_cache()
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

    async def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve data from Redis cache."""
        try:
            if self.redis and self.redis.enabled():
                cached_data = self.redis.get(key)
                if cached_data:
                    logger.info(f"Retrieved news from cache: {key}")
                    return cached_data
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        return None

    async def _save_to_cache(self, key: str, data: List[Dict[str, Any]]) -> None:
        """Save data to Redis cache."""
        try:
            if self.redis and self.redis.enabled():
                self.redis.set(key, data, ttl=self.cache_ttl)
                logger.info(f"Cached news data: {key}")
        except Exception as e:
            logger.warning(f"Cache save error: {e}")

    async def get_general_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get general market news.

        Args:
            limit: Maximum number of articles to return (default: 50)

        Returns:
            List of news articles
        """
        cache_key = "news:general"

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]

        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not configured")
            return []

        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/news"
                params = {"category": "general", "token": self.finnhub_api_key}

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Filter news from last 7 days
                filtered_news = self._filter_recent_news(data, days=7)

                # Cache the results
                await self._save_to_cache(cache_key, filtered_news)

                return filtered_news[:limit]

        except httpx.HTTPError as e:
            logger.error(f"Error fetching general news from Finnhub: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching general news: {e}", exc_info=True)
            return []

    async def get_company_news(
        self, ticker: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get company-specific news.

        Args:
            ticker: Company ticker symbol
            limit: Maximum number of articles to return (default: 50)

        Returns:
            List of news articles for the company
        """
        ticker = ticker.upper()
        cache_key = f"news:company:{ticker}"

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]

        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not configured")
            return []

        try:
            await self._rate_limit()

            # Calculate date range (last 7 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/company-news"
                params = {
                    "symbol": ticker,
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "token": self.finnhub_api_key,
                }

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Filter news from last 7 days (API may return more)
                filtered_news = self._filter_recent_news(data, days=7)

                # Cache the results
                await self._save_to_cache(cache_key, filtered_news)

                return filtered_news[:limit]

        except httpx.HTTPError as e:
            logger.error(f"Error fetching company news for {ticker} from Finnhub: {e}")
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error fetching company news for {ticker}: {e}",
                exc_info=True,
            )
            return []

    async def get_crypto_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get crypto news.

        Args:
            limit: Maximum number of articles to return (default: 50)

        Returns:
            List of crypto news articles
        """
        cache_key = "news:crypto"

        # Check cache first
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]

        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not configured")
            return []

        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/news"
                params = {"category": "crypto", "token": self.finnhub_api_key}

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Filter news from last 7 days
                filtered_news = self._filter_recent_news(data, days=7)

                # Cache the results
                await self._save_to_cache(cache_key, filtered_news)

                return filtered_news[:limit]

        except httpx.HTTPError as e:
            logger.error(f"Error fetching crypto news from Finnhub: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching crypto news: {e}", exc_info=True)
            return []

    async def get_latest_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest news from all categories (general, company, crypto).

        Args:
            limit: Maximum number of articles to return (default: 50)

        Returns:
            Combined list of latest news articles
        """
        # Fetch from all categories
        general_news = await self.get_general_news(limit=limit)
        crypto_news = await self.get_crypto_news(limit=limit)

        # Combine and sort by datetime (most recent first)
        all_news = general_news + crypto_news

        # Sort by datetime (Unix timestamp)
        all_news.sort(key=lambda x: x.get("datetime", 0), reverse=True)

        # Remove duplicates based on headline
        seen_headlines = set()
        unique_news = []
        for article in all_news:
            headline = article.get("headline", "")
            if headline and headline not in seen_headlines:
                seen_headlines.add(headline)
                unique_news.append(article)

        return unique_news[:limit]

    def _filter_recent_news(
        self, news_data: List[Dict[str, Any]], days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Filter news articles to only include those from the last N days.

        Args:
            news_data: List of news articles from API
            days: Number of days to look back (default: 7)

        Returns:
            Filtered list of news articles
        """
        if not isinstance(news_data, list):
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = int(cutoff_date.timestamp())

        filtered = []
        for article in news_data:
            # Get datetime (Unix timestamp)
            article_datetime = article.get("datetime", 0)

            # Only include articles from the last N days
            if article_datetime >= cutoff_timestamp:
                filtered.append(article)

        # Sort by datetime (most recent first)
        filtered.sort(key=lambda x: x.get("datetime", 0), reverse=True)

        return filtered
