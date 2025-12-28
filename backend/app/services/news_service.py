"""
News Service

Fetches and manages market news articles from Finnhub News API.
Implements on-demand fetching, rate limiting, and Supabase caching.

Data Sources:
- Finnhub News API (general market news, company news, crypto news)
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings
from app.services.supabase_cache_service import supabase_cache_service

logger = logging.getLogger(__name__)


class NewsService:
    """
    Service for fetching and managing market news.
    
    Fetches news on-demand from Finnhub API with Supabase caching.
    Replaces Celery-based background fetching.
    """

    def __init__(self):
        """Initialize the news service."""
        self.cache_ttl_minutes = 15  # 15 minutes cache TTL
        self.finnhub_api_key = getattr(settings, "finnhub_api_key", None)
        self.rate_limit = 60  # Finnhub free tier: 60 calls/minute
        self.base_url = "https://finnhub.io/api/v1"
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

    async def _fetch_general_news(self) -> List[Dict[str, Any]]:
        """Fetch general market news from Finnhub API."""
        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not configured for general news.")
            return []

        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/news"
                params = {"category": "general", "token": self.finnhub_api_key}
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                filtered_news = self._filter_recent_news(data, days=7)
                logger.info(f"Fetched {len(filtered_news)} general news articles from Finnhub")
                return filtered_news

        except httpx.HTTPStatusError as e:
            logger.error(f"Finnhub HTTP error for general news: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Finnhub request error for general news: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching general news: {e}", exc_info=True)
            return []

    async def _fetch_crypto_news(self) -> List[Dict[str, Any]]:
        """Fetch crypto news from Finnhub API."""
        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not configured for crypto news.")
            return []

        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/news"
                params = {"category": "crypto", "token": self.finnhub_api_key}
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                filtered_news = self._filter_recent_news(data, days=7)
                logger.info(f"Fetched {len(filtered_news)} crypto news articles from Finnhub")
                return filtered_news

        except httpx.HTTPStatusError as e:
            logger.error(f"Finnhub HTTP error for crypto news: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Finnhub request error for crypto news: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching crypto news: {e}", exc_info=True)
            return []

    async def _fetch_company_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch company-specific news from Finnhub API."""
        if not self.finnhub_api_key:
            logger.warning(f"Finnhub API key not configured for company news ({ticker}).")
            return []

        ticker = ticker.upper()
        try:
            await self._rate_limit()

            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/company-news"
                to_date = datetime.now()
                from_date = to_date - timedelta(days=7)
                params = {
                    "symbol": ticker,
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "token": self.finnhub_api_key
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                filtered_news = self._filter_recent_news(data, days=7)
                logger.info(f"Fetched {len(filtered_news)} company news articles for {ticker} from Finnhub")
                return filtered_news

        except httpx.HTTPStatusError as e:
            logger.error(f"Finnhub HTTP error for company news ({ticker}): {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Finnhub request error for company news ({ticker}): {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching company news for {ticker}: {e}", exc_info=True)
            return []

    async def get_general_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get general market news (on-demand fetch with caching).
        """
        cache_key = "news:general"
        
        # Use get_or_set pattern: check cache, fetch if miss
        async def fetch_func():
            return await self._fetch_general_news()
        
        news = await supabase_cache_service.get_or_set(
            cache_key,
            fetch_func,
            ttl_minutes=self.cache_ttl_minutes,
            cache_type="news"
        )
        
        return news[:limit] if news else []

    async def get_company_news(
        self, ticker: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get company-specific news (on-demand fetch with caching).
        """
        ticker = ticker.upper()
        cache_key = f"news:company:{ticker}"
        
        # Use get_or_set pattern: check cache, fetch if miss
        async def fetch_func():
            return await self._fetch_company_news(ticker)
        
        news = await supabase_cache_service.get_or_set(
            cache_key,
            fetch_func,
            ttl_minutes=self.cache_ttl_minutes,
            cache_type="news"
        )
        
        return news[:limit] if news else []

    async def get_crypto_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get crypto news (on-demand fetch with caching).
        """
        cache_key = "news:crypto"
        
        # Use get_or_set pattern: check cache, fetch if miss
        async def fetch_func():
            return await self._fetch_crypto_news()
        
        news = await supabase_cache_service.get_or_set(
            cache_key,
            fetch_func,
            ttl_minutes=self.cache_ttl_minutes,
            cache_type="news"
        )
        
        return news[:limit] if news else []

    async def get_latest_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest news from all categories (general, company, crypto).
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


