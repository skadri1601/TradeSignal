"""
News Service

Fetches and manages market news articles from Finnhub News API.
Implements rate limiting, Redis caching, and error handling.

Data Sources:
- Finnhub News API (general market news, company news, crypto news)
"""

import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.core.redis_cache import get_cache

logger = logging.getLogger(__name__)


class NewsService:
    """
    Service for fetching and managing market news.

    This service primarily reads from a Redis cache which is populated by Celery tasks.
    """

    def __init__(self):
        """Initialize the news service."""
        self.cache_ttl = 21600  # 6 hours in seconds (should match Celery task)
        self.redis = get_cache()

    async def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve data from Redis cache."""
        try:
            if self.redis and self.redis.enabled():
                cached_data = self.redis.get(key)
                if cached_data:
                    logger.debug(f"Retrieved news from cache: {key}")
                    return cached_data
        except Exception as e:
            logger.warning(f"Cache retrieval error for {key}: {e}")
        return None

    async def get_general_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get general market news from cache.
        """
        cache_key = "news:general"
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]
        logger.warning(f"General news cache miss for key: {cache_key}")
        return []

    async def get_company_news(
        self, ticker: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get company-specific news from cache.
        """
        ticker = ticker.upper()
        cache_key = f"news:company:{ticker}"
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]
        logger.warning(f"Company news cache miss for key: {cache_key} (ticker: {ticker})")
        return []

    async def get_crypto_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get crypto news from cache.
        """
        cache_key = "news:crypto"
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]
        logger.warning(f"Crypto news cache miss for key: {cache_key}")
        return []

    async def get_latest_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest news from all categories (general, company, crypto) from cache.
        """
        general_news = await self.get_general_news(limit=limit)
        crypto_news = await self.get_crypto_news(limit=limit)

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


