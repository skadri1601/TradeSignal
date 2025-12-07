"""
Congressional Trade API Client.

Fetches congressional stock trading data from Finnhub API with fallback sources.
Implements rate limiting, caching, and error handling.
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Any
from decimal import Decimal
import httpx

from app.config import settings
from app.core.redis_cache import get_cache

logger = logging.getLogger(__name__)


class CongressionalAPIClient:
    """
    Client for fetching congressional trading data.

    Primary source: Finnhub Congressional Trading API (free tier)
    Implements rate limiting and Redis caching.
    """

    def __init__(self):
        """Initialize the congressional API client."""
        self.finnhub_api_key = settings.finnhub_api_key
        self.rate_limit = settings.congressional_rate_limit  # requests per minute
        self.cache_ttl = (
            settings.congressional_cache_ttl_hours * 3600
        )  # convert to seconds
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

    async def fetch_congressional_trades(
        self,
        symbol: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch congressional trades from Finnhub API.

        Args:
            symbol: Stock ticker (optional, fetches all if not specified)
            from_date: Start date (defaults to 60 days ago)
            to_date: End date (defaults to today)

        Returns:
            List of congressional trade dictionaries

        Raises:
            httpx.HTTPError: If API request fails
        """
        # Set default date range
        if not to_date:
            to_date = date.today()
        if not from_date:
            from_date = to_date - timedelta(
                days=settings.congressional_scrape_days_back
            )

        # Check cache first
        cache_key = f"congress:trades:{symbol or 'all'}:{from_date}:{to_date}"
        cached = await self._get_from_cache(cache_key)
        if cached:
            logger.info(f"Retrieved {len(cached)} congressional trades from cache")
            return cached

        # Try Finnhub API first (if key is configured)
        if self.finnhub_api_key:
            try:
                trades = await self._fetch_from_finnhub(symbol, from_date, to_date)

                # Cache the results
                await self._save_to_cache(cache_key, trades)

                logger.info(
                    f"Fetched {len(trades)} congressional trades from Finnhub API"
                )
                return trades
            except Exception as e:
                logger.warning(f"Finnhub API failed: {e}, trying free alternatives...")
        else:
            logger.info("Finnhub API key not configured, using free alternatives...")

        # Try fallback sources (free alternatives)
        trades = await self._fetch_fallback(symbol, from_date, to_date)

        # Cache the results even from fallback
        if trades:
            await self._save_to_cache(cache_key, trades)

        return trades

    async def _fetch_from_finnhub(
        self, symbol: Optional[str], from_date: date, to_date: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch from Finnhub Congressional Trading API.

        API Endpoint: GET /stock/congressional-trading
        Free tier: 60 calls/minute
        """
        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not configured")
            return []

        await self._rate_limit()

        params = {
            "token": self.finnhub_api_key,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        if symbol:
            params["symbol"] = symbol.upper()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/stock/congressional-trading",
                params=params,
                headers={"User-Agent": settings.sec_user_agent},
            )
            response.raise_for_status()
            data = response.json()

        # Parse Finnhub response
        trades = []
        if "data" in data and data["data"]:
            for item in data["data"]:
                trade = self._parse_finnhub_trade(item)
                if trade:
                    trades.append(trade)

        return trades

    def _parse_finnhub_trade(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Finnhub congressional trade data into standardized format.

        Finnhub format:
        {
            "symbol": "AAPL",
            "name": "Rep. John Doe",
            "transactionDate": "2024-01-15",
            "transactionType": "Purchase",
            "amount": "$1,001 - $15,000",
            "assetDescription": "Apple Inc - Common Stock",
            "assetType": "Stock",
            "position": "Member",
            "owner": "Self",
            "filingDate": "2024-01-20"
        }
        """
        try:
            # Parse amount range
            amount_min, amount_max = self._parse_amount_range(item.get("amount", ""))
            amount_estimated = None
            if amount_min and amount_max:
                amount_estimated = (amount_min + amount_max) / 2

            # Determine transaction type
            transaction_type = "BUY"
            tx_type_raw = str(item.get("transactionType", "")).lower()
            if "sale" in tx_type_raw or "sell" in tx_type_raw:
                transaction_type = "SELL"

            # Extract chamber and party from name/position (if available)
            name = item.get("name", "")
            chamber = self._extract_chamber(name, item.get("position", ""))

            return {
                "name": name,
                "ticker": item.get("symbol"),
                "asset_description": item.get(
                    "assetDescription", item.get("assetName", "")
                ),
                "transaction_date": item.get("transactionDate"),
                "disclosure_date": item.get("filingDate", item.get("transactionDate")),
                "transaction_type": transaction_type,
                "amount_min": float(amount_min) if amount_min else None,
                "amount_max": float(amount_max) if amount_max else None,
                "amount_estimated": float(amount_estimated)
                if amount_estimated
                else None,
                "owner_type": item.get("owner", "Self"),
                "asset_type": item.get("assetType", "Stock"),
                "chamber": chamber,
                "source": "finnhub",
                "raw_data": item,  # Store raw for debugging
            }
        except Exception as e:
            logger.error(f"Error parsing Finnhub trade: {e}, data: {item}")
            return None

    def _parse_amount_range(
        self, amount_str: str
    ) -> tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Parse amount range string like "$1,001 - $15,000" or "$1,001-$15,000".

        Returns:
            Tuple of (min_amount, max_amount) as Decimal
        """
        if not amount_str:
            return None, None

        try:
            # Remove $ and commas
            amount_str = amount_str.replace("$", "").replace(",", "").strip()

            # Split on dash/hyphen
            if "-" in amount_str:
                parts = amount_str.split("-")
                if len(parts) == 2:
                    min_val = Decimal(parts[0].strip())
                    max_val = Decimal(parts[1].strip())
                    return min_val, max_val

            # Single value (rare)
            return Decimal(amount_str), Decimal(amount_str)
        except Exception as e:
            logger.warning(f"Could not parse amount range '{amount_str}': {e}")
            return None, None

    def _extract_chamber(self, name: str, position: str) -> str:
        """
        Extract chamber (HOUSE or SENATE) from name or position.

        Args:
            name: Congressperson name (may include "Rep." or "Sen.")
            position: Position/title

        Returns:
            "HOUSE" or "SENATE"
        """
        name_lower = name.lower()
        position_lower = position.lower()

        if (
            "sen." in name_lower
            or "senator" in name_lower
            or "senator" in position_lower
        ):
            return "SENATE"
        elif (
            "rep." in name_lower
            or "representative" in name_lower
            or "representative" in position_lower
        ):
            return "HOUSE"

        # Default to HOUSE if unclear
        return "HOUSE"

    async def _fetch_fallback(
        self, symbol: Optional[str], from_date: date, to_date: date
    ) -> List[Dict[str, Any]]:
        """
        Fallback to alternative FREE data sources if Finnhub fails.

        Tries in order:
        1. Senate Stock Watcher API
        2. House Stock Watcher API
        3. Stocksera API (if available)
        """
        logger.info("Finnhub API failed, trying free alternative sources...")

        all_trades = []

        # Try Senate Stock Watcher
        try:
            logger.info("Fetching from Senate Stock Watcher...")
            senate_trades = await self._fetch_from_senate_stock_watcher(
                symbol, from_date, to_date
            )
            if senate_trades:
                all_trades.extend(senate_trades)
                logger.info(
                    f"Fetched {len(senate_trades)} trades from Senate Stock Watcher"
                )
        except Exception as e:
            logger.warning(f"Senate Stock Watcher failed: {e}")

        # Try House Stock Watcher
        try:
            logger.info("Fetching from House Stock Watcher...")
            house_trades = await self._fetch_from_house_stock_watcher(
                symbol, from_date, to_date
            )
            if house_trades:
                all_trades.extend(house_trades)
                logger.info(
                    f"Fetched {len(house_trades)} trades from House Stock Watcher"
                )
        except Exception as e:
            logger.warning(f"House Stock Watcher failed: {e}")

        if all_trades:
            logger.info(
                f"Successfully fetched {len(all_trades)} trades from free alternative sources"
            )
        else:
            logger.warning("All free alternative sources failed or returned no data")

        return all_trades

    async def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve data from Redis cache."""
        try:
            if self.redis:
                cached_data = self.redis.get(key)
                if cached_data:
                    return cached_data  # RedisCache.get() already returns parsed dict
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        return None

    async def _save_to_cache(self, key: str, data: List[Dict[str, Any]]) -> None:
        """Save data to Redis cache."""
        try:
            if self.redis:
                self.redis.set(key, data, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Cache save error: {e}")

    async def _fetch_from_senate_stock_watcher(
        self, symbol: Optional[str], from_date: date, to_date: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch congressional trades from Senate Stock Watcher API (FREE).

        API: https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json
        Or: https://housestockwatcher.com/api/senate
        """
        try:
            # Try multiple endpoints
            endpoints = [
                "https://housestockwatcher.com/api/senate",
                "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json",
            ]

            for endpoint in endpoints:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(
                            endpoint, headers={"User-Agent": settings.sec_user_agent}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            trades = self._parse_stock_watcher_data(
                                data, "SENATE", symbol, from_date, to_date
                            )
                            if trades:
                                return trades
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue

            return []
        except Exception as e:
            logger.error(f"Error fetching from Senate Stock Watcher: {e}")
            return []

    async def _fetch_from_house_stock_watcher(
        self, symbol: Optional[str], from_date: date, to_date: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch congressional trades from House Stock Watcher API (FREE).

        Multiple endpoints to try:
        - https://housestockwatcher.com/api/house
        - https://house-stock-watcher.com/api/all
        - GitHub repos with public data
        """
        try:
            # Try multiple endpoints
            endpoints = [
                "https://housestockwatcher.com/api/house",
                "https://house-stock-watcher.com/api/all",
                "https://housestockwatcher.com/api/all",
            ]

            for endpoint in endpoints:
                try:
                    async with httpx.AsyncClient(
                        timeout=30.0, follow_redirects=True
                    ) as client:
                        response = await client.get(
                            endpoint,
                            headers={
                                "User-Agent": settings.sec_user_agent,
                                "Accept": "application/json",
                            },
                        )
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                trades = self._parse_stock_watcher_data(
                                    data, "HOUSE", symbol, from_date, to_date
                                )
                                if trades:
                                    logger.info(f"Successfully fetched from {endpoint}")
                                    return trades
                            except Exception as e:
                                logger.debug(
                                    f"Failed to parse JSON from {endpoint}: {e}"
                                )
                                continue
                except httpx.HTTPError as e:
                    logger.debug(f"HTTP error for {endpoint}: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue

            # Try GitHub-based sources (more reliable)
            github_endpoints = [
                (
                    "https://raw.githubusercontent.com/timothycarambat/"
                    "senate-stock-watcher-data/main/aggregate/all_transactions.json"
                ),
                (
                    "https://raw.githubusercontent.com/washingtonpost/"
                    "data-congressional-stock-trading/main/all_transactions.json"
                ),
            ]

            for endpoint in github_endpoints:
                try:
                    async with httpx.AsyncClient(
                        timeout=30.0, follow_redirects=True
                    ) as client:
                        response = await client.get(
                            endpoint, headers={"User-Agent": settings.sec_user_agent}
                        )
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                # Filter for House only
                                if isinstance(data, list):
                                    house_data = [
                                        item
                                        for item in data
                                        if self._is_house_member(item)
                                    ]
                                    trades = self._parse_stock_watcher_data(
                                        house_data, "HOUSE", symbol, from_date, to_date
                                    )
                                    if trades:
                                        logger.info(
                                            f"Successfully fetched {len(trades)} trades from GitHub: {endpoint}"
                                        )
                                        return trades
                            except Exception as e:
                                logger.debug(
                                    f"Failed to parse JSON from GitHub {endpoint}: {e}"
                                )
                                continue
                except Exception as e:
                    logger.debug(f"GitHub endpoint {endpoint} failed: {e}")
                    continue

            return []
        except Exception as e:
            logger.error(f"Error fetching from House Stock Watcher: {e}")
            return []

    def _parse_stock_watcher_data(
        self,
        data: Any,
        chamber: str,
        symbol: Optional[str],
        from_date: date,
        to_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Parse Stock Watcher API data into standardized format.

        Expected format (varies by source):
        - Array of trade objects
        - Each object has: name, ticker, transaction_date, type, amount, etc.
        """
        trades = []

        # Handle different response formats
        if isinstance(data, dict):
            # Try common keys
            items = data.get("data", data.get("trades", data.get("transactions", [])))
        elif isinstance(data, list):
            items = data
        else:
            logger.warning(f"Unexpected data format from Stock Watcher: {type(data)}")
            return []

        for item in items:
            try:
                # Parse transaction date
                tx_date_str = (
                    item.get("transaction_date")
                    or item.get("date")
                    or item.get("transactionDate")
                )
                if not tx_date_str:
                    continue

                # Parse date (handle multiple formats)
                tx_date = self._parse_date(tx_date_str)
                if not tx_date:
                    continue

                # Filter by date range
                if tx_date < from_date or tx_date > to_date:
                    continue

                # Filter by symbol if specified
                ticker = item.get("ticker") or item.get("symbol") or item.get("stock")
                if symbol and ticker and ticker.upper() != symbol.upper():
                    continue

                # Parse transaction type
                tx_type_raw = str(
                    item.get("type")
                    or item.get("transaction_type")
                    or item.get("transactionType")
                    or ""
                ).lower()
                transaction_type = "BUY"
                if (
                    "sale" in tx_type_raw
                    or "sell" in tx_type_raw
                    or "sold" in tx_type_raw
                ):
                    transaction_type = "SELL"

                # Parse amount
                amount_str = (
                    item.get("amount")
                    or item.get("value")
                    or item.get("transaction_amount")
                    or ""
                )
                amount_min, amount_max = self._parse_amount_range(amount_str)
                amount_estimated = None
                if amount_min and amount_max:
                    amount_estimated = float((amount_min + amount_max) / 2)
                elif amount_min:
                    amount_estimated = float(amount_min)

                # Get name
                name = (
                    item.get("name")
                    or item.get("representative")
                    or item.get("senator")
                    or item.get("member")
                    or ""
                )

                # Get owner type
                owner_type = (
                    item.get("owner")
                    or item.get("owner_type")
                    or item.get("ownerType")
                    or "Self"
                )

                # Get asset description
                asset_desc = (
                    item.get("asset_description")
                    or item.get("assetDescription")
                    or item.get("description")
                    or item.get("stock")
                    or ""
                )

                trade = {
                    "name": name,
                    "ticker": ticker,
                    "asset_description": asset_desc,
                    "transaction_date": tx_date.isoformat(),
                    "disclosure_date": item.get("disclosure_date")
                    or item.get("filing_date")
                    or item.get("filingDate")
                    or tx_date.isoformat(),
                    "transaction_type": transaction_type,
                    "amount_min": float(amount_min) if amount_min else None,
                    "amount_max": float(amount_max) if amount_max else None,
                    "amount_estimated": amount_estimated,
                    "owner_type": owner_type,
                    "asset_type": item.get("asset_type")
                    or item.get("assetType")
                    or "Stock",
                    "chamber": chamber,
                    "source": "stock_watcher",
                    "raw_data": item,
                }

                trades.append(trade)

            except Exception as e:
                logger.warning(f"Error parsing Stock Watcher trade: {e}, item: {item}")
                continue

        return trades

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string in various formats."""
        if not date_str:
            return None

        # Common date formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def _is_senate_member(self, item: Dict[str, Any]) -> bool:
        """Check if item is a Senate member trade."""
        chamber = str(item.get("chamber", "")).upper()
        name = str(item.get("name", "")).lower()
        if chamber == "SENATE" or "sen." in name or "senator" in name:
            return True
        return False

    def _is_house_member(self, item: Dict[str, Any]) -> bool:
        """Check if item is a House member trade."""
        chamber = str(item.get("chamber", "")).upper()
        name = str(item.get("name", "")).lower()
        if chamber == "HOUSE" or "rep." in name or "representative" in name:
            return True
        return False
