"""
Stock Price Service - Multi-Source Live Data Integration

Fetches live stock prices with intelligent fallback:
1. Yahoo Finance (primary - free, no API key needed)
2. Alpha Vantage (fallback - requires API key)
3. Stale cache (if all APIs fail)

Uses 60-second caching to minimize API requests and avoid rate limiting.
NO DEMO DATA - Only live data from real APIs.
"""

import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Company
from app.config import settings
from alpha_vantage.timeseries import TimeSeries
import finnhub
from prometheus_client import Counter, Histogram

# NOTE: Redis cache removed - using in-memory cache only

logger = logging.getLogger(__name__)

# Prometheus metrics
QUOTE_FETCH_COUNTER = Counter(
    "stock_quote_fetches_total",
    "Total stock quote fetches",
    ["ticker", "source", "status"],
)

QUOTE_FETCH_DURATION = Histogram(
    "stock_quote_fetch_duration_seconds",
    "Stock quote fetch duration seconds",
    ["ticker", "source"],
)

CACHE_HIT_COUNTER = Counter("cache_hits_total", "Total cache hits", ["cache_type"])

# Rate limiting
_last_yahoo_request_time = 0
_last_alpha_vantage_request_time = 0
_last_finnhub_request_time = 0
_min_yahoo_interval = 1.0  # 1 second between Yahoo requests (increased from 0.2s to reduce rate limiting)
_min_alpha_vantage_interval = (
    12.0  # 12 seconds between Alpha Vantage requests (5 per minute limit)
)
_min_finnhub_interval = 1.0  # 1 second between Finnhub requests (60 per minute limit)

# Cache for stock quotes (ticker -> (quote_data, timestamp))
_quote_cache: Dict[str, tuple[Dict[str, Any], float]] = {}
_cache_ttl = (
    60  # Cache quotes for 60 seconds (reduced from 10s to minimize API calls)
)

# Cache for price history (ticker_days -> (history_data, timestamp))
_price_history_cache: Dict[str, tuple[List[Dict[str, Any]], float]] = {}
_price_history_cache_ttl = 300  # Cache price history for 5 minutes (300 seconds)

# Track consecutive failures to switch data sources
_yahoo_consecutive_failures = 0
_finnhub_consecutive_failures = 0
_alpha_vantage_consecutive_failures = 0
_max_yahoo_failures_before_fallback = 3


class StockPriceService:
    """Service for fetching live stock prices with intelligent multi-source fallback."""

    @staticmethod
    def _rate_limit_yahoo():
        """Apply rate limiting for Yahoo Finance requests."""
        global _last_yahoo_request_time
        current_time = time.time()
        time_since_last = current_time - _last_yahoo_request_time

        if time_since_last < _min_yahoo_interval:
            time.sleep(_min_yahoo_interval - time_since_last)

        _last_yahoo_request_time = time.time()

    @staticmethod
    def _rate_limit_alpha_vantage():
        """Apply rate limiting for Alpha Vantage requests (5 calls per minute limit)."""
        global _last_alpha_vantage_request_time
        current_time = time.time()
        time_since_last = current_time - _last_alpha_vantage_request_time

        if time_since_last < _min_alpha_vantage_interval:
            wait_time = _min_alpha_vantage_interval - time_since_last
            logger.info(f"Rate limiting Alpha Vantage: waiting {wait_time:.1f}s")
            time.sleep(wait_time)

        _last_alpha_vantage_request_time = time.time()

    @staticmethod
    def _rate_limit_finnhub():
        """Apply rate limiting for Finnhub requests (60 calls per minute limit)."""
        global _last_finnhub_request_time
        current_time = time.time()
        time_since_last = current_time - _last_finnhub_request_time

        if time_since_last < _min_finnhub_interval:
            time.sleep(_min_finnhub_interval - time_since_last)

        _last_finnhub_request_time = time.time()

    @staticmethod
    def _fetch_from_yahoo(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch stock quote from Yahoo Finance.

        Returns quote data or None if failed.
        """
        global _yahoo_consecutive_failures

        try:
            StockPriceService._rate_limit_yahoo()

            # Use Ticker without custom session - yfinance handles this internally
            stock = yf.Ticker(ticker)

            # Try fast_info first (faster and more reliable)
            try:
                info = stock.fast_info
                current_price = float(info.last_price)
                previous_close = (
                    float(info.previous_close)
                    if hasattr(info, "previous_close")
                    else current_price
                )

                price_change = current_price - previous_close
                price_change_percent = (
                    (price_change / previous_close) * 100 if previous_close else 0
                )

                # Get market cap and convert to integer
                market_cap = getattr(info, "market_cap", None)
                if market_cap is not None:
                    market_cap = int(float(market_cap))

                # Get volume and convert to integer
                volume = getattr(info, "last_volume", None)
                if volume is not None:
                    volume = int(float(volume))

                quote_data = {
                    "ticker": ticker,
                    "current_price": round(current_price, 2),
                    "previous_close": round(previous_close, 2),
                    "price_change": round(price_change, 2),
                    "price_change_percent": round(price_change_percent, 2),
                    "market_cap": market_cap,
                    "volume": volume,
                    "avg_volume": None,
                    "day_high": getattr(info, "day_high", None),
                    "day_low": getattr(info, "day_low", None),
                    "fifty_two_week_high": getattr(info, "year_high", None),
                    "fifty_two_week_low": getattr(info, "year_low", None),
                    "market_state": "REGULAR",
                    "updated_at": datetime.utcnow().isoformat(),
                }

                # Reset failure counter on success
                _yahoo_consecutive_failures = 0
                logger.info(
                    f"Successfully fetched {ticker} from Yahoo Finance (fast_info)"
                )
                return quote_data

            except Exception as fast_info_error:
                logger.debug(
                    f"fast_info failed for {ticker}, trying history: {fast_info_error}"
                )

                # Fallback to historical data method
                hist = stock.history(period="5d")

                if hist.empty:
                    logger.warning(f"No historical data returned for {ticker}")
                    raise ValueError("Empty history data")

                # Get most recent data
                latest = hist.iloc[-1]
                current_price = float(latest["Close"])

                # Calculate previous close and changes
                if len(hist) > 1:
                    previous = hist.iloc[-2]
                    previous_close = float(previous["Close"])
                else:
                    previous_close = float(latest["Open"])

                price_change = current_price - previous_close
                price_change_percent = (
                    (price_change / previous_close) * 100 if previous_close else 0
                )

                # Try to get additional info
                market_cap = None
                try:
                    info_dict = stock.info
                    market_cap = info_dict.get("marketCap")
                    if market_cap is not None:
                        market_cap = int(float(market_cap))
                except Exception:
                    pass

                quote_data = {
                    "ticker": ticker,
                    "current_price": round(current_price, 2),
                    "previous_close": round(previous_close, 2),
                    "price_change": round(price_change, 2),
                    "price_change_percent": round(price_change_percent, 2),
                    "market_cap": market_cap,
                    "volume": int(latest["Volume"]) if "Volume" in latest else None,
                    "avg_volume": None,
                    "day_high": round(float(latest["High"]), 2)
                    if "High" in latest
                    else None,
                    "day_low": round(float(latest["Low"]), 2)
                    if "Low" in latest
                    else None,
                    "fifty_two_week_high": None,
                    "fifty_two_week_low": None,
                    "market_state": "REGULAR",
                    "updated_at": datetime.utcnow().isoformat(),
                }

                # Reset failure counter on success
                _yahoo_consecutive_failures = 0
                logger.info(
                    f"Successfully fetched {ticker} from Yahoo Finance (history)"
                )
                return quote_data

        except Exception as e:
            _yahoo_consecutive_failures += 1
            logger.error(
                f"Yahoo Finance failed for {ticker} (failure #{_yahoo_consecutive_failures}): {e}"
            )
            return None

    @staticmethod
    def _fetch_from_alpha_vantage(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch stock quote from Alpha Vantage API.

        Returns quote data or None if failed/not configured.
        """
        if not settings.alpha_vantage_api_key:
            logger.debug("Alpha Vantage API key not configured")
            return None

        try:
            StockPriceService._rate_limit_alpha_vantage()

            # Initialize Alpha Vantage client
            ts = TimeSeries(key=settings.alpha_vantage_api_key, output_format="json")

            # Get quote data
            data, meta_data = ts.get_quote_endpoint(symbol=ticker)

            if not data or "01. symbol" not in data:
                logger.warning(f"Invalid response from Alpha Vantage for {ticker}")
                return None

            current_price = float(data["05. price"])
            previous_close = float(data["08. previous close"])
            price_change = float(data["09. change"])
            price_change_percent = float(data["10. change percent"].rstrip("%"))

            quote_data = {
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "market_cap": None,  # Not available in quote endpoint
                "volume": int(data["06. volume"]) if "06. volume" in data else None,
                "avg_volume": None,
                "day_high": round(float(data["03. high"]), 2)
                if "03. high" in data
                else None,
                "day_low": round(float(data["04. low"]), 2)
                if "04. low" in data
                else None,
                "fifty_two_week_high": round(float(data["52. week high"]), 2)
                if "52. week high" in data
                else None,
                "fifty_two_week_low": round(float(data["52. week low"]), 2)
                if "52. week low" in data
                else None,
                "market_state": "REGULAR",
                "updated_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Successfully fetched {ticker} from Alpha Vantage")
            return quote_data

        except Exception as e:
            global _alpha_vantage_consecutive_failures
            _alpha_vantage_consecutive_failures += 1
            logger.error(
                f"Alpha Vantage failed for {ticker} (failure #{_alpha_vantage_consecutive_failures}): {e}"
            )
            return None

    @staticmethod
    def _fetch_from_finnhub(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch stock quote from Finnhub API (FREE tier: 60 calls/min).

        Returns quote data or None if failed/not configured.
        """
        global _finnhub_consecutive_failures

        if not settings.finnhub_api_key:
            logger.debug("Finnhub API key not configured")
            return None

        try:
            StockPriceService._rate_limit_finnhub()

            # Initialize Finnhub client
            finnhub_client = finnhub.Client(api_key=settings.finnhub_api_key)

            # Get quote data
            quote = finnhub_client.quote(ticker)

            if not quote or "c" not in quote:
                logger.warning(f"Invalid response from Finnhub for {ticker}")
                return None

            current_price = float(quote["c"])  # Current price
            previous_close = float(quote["pc"])  # Previous close
            price_change = current_price - previous_close
            price_change_percent = (
                (price_change / previous_close) * 100 if previous_close else 0
            )

            quote_data = {
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "market_cap": None,  # Not available in basic quote
                "volume": None,
                "avg_volume": None,
                "day_high": round(float(quote["h"]), 2)
                if "h" in quote and quote["h"]
                else None,  # High price of the day
                "day_low": round(float(quote["l"]), 2)
                if "l" in quote and quote["l"]
                else None,  # Low price of the day
                "fifty_two_week_high": None,
                "fifty_two_week_low": None,
                "market_state": "REGULAR",
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Reset failure counter on success
            _finnhub_consecutive_failures = 0
            logger.info(f"Successfully fetched {ticker} from Finnhub")
            return quote_data

        except Exception as e:
            _finnhub_consecutive_failures += 1
            logger.error(
                f"Finnhub failed for {ticker} (failure #{_finnhub_consecutive_failures}): {e}"
            )
            return None

    @staticmethod
    def get_stock_quote(
        ticker: str, use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get current stock quote with intelligent multi-source fallback.

        Tries data sources in order:
        1. Cache (if enabled and fresh)
        2. Yahoo Finance (primary, free)
        3. Alpha Vantage (fallback if Yahoo fails repeatedly)
        4. Stale cache (if APIs fail)

        Args:
            ticker: Stock ticker symbol
            use_cache: Whether to use cached data (default True)

        Returns:
            Dict with price data including staleness indicators or None if all sources failed
        """
        # Check in-memory cache (Redis removed)
        if use_cache and ticker in _quote_cache:
            cached_data, cached_time = _quote_cache[ticker]
            age_seconds = int(time.time() - cached_time)

            if age_seconds < _cache_ttl:
                logger.debug(
                    f"Using in-memory cached data for {ticker} (age: {age_seconds}s)"
                )
                # Add staleness metadata for cached data
                cached_data["is_stale"] = age_seconds > 60
                cached_data["data_age_seconds"] = age_seconds
                cached_data["last_updated"] = datetime.fromtimestamp(
                    cached_time
                ).isoformat()
                cached_data["cached"] = True
                cached_data["data_source"] = cached_data.get(
                    "data_source", "yahoo_finance"
                )
                try:
                    CACHE_HIT_COUNTER.labels(cache_type="memory").inc()
                except Exception:
                    pass
                return cached_data

        # Try Yahoo Finance first
        # Time the fetch from Yahoo
        with QUOTE_FETCH_DURATION.labels(ticker=ticker, source="yahoo").time():
            quote = StockPriceService._fetch_from_yahoo(ticker)

        if quote:
            try:
                QUOTE_FETCH_COUNTER.labels(
                    ticker=ticker, source="yahoo", status="success"
                ).inc()
            except Exception:
                pass

        if quote:
            # Add staleness metadata for fresh data
            quote["is_stale"] = False
            quote["data_age_seconds"] = 0
            quote["last_updated"] = datetime.now().isoformat()
            quote["cached"] = False
            quote["data_source"] = "yahoo_finance"

        # If Yahoo fails repeatedly, try Finnhub
        if (
            not quote
            and _yahoo_consecutive_failures >= _max_yahoo_failures_before_fallback
        ):
            logger.info(
                f"Yahoo Finance has failed {_yahoo_consecutive_failures} times, trying Finnhub"
            )
            with QUOTE_FETCH_DURATION.labels(ticker=ticker, source="finnhub").time():
                quote = StockPriceService._fetch_from_finnhub(ticker)

            if quote:
                # Add staleness metadata for Finnhub data
                quote["is_stale"] = False
                quote["data_age_seconds"] = 0
                quote["last_updated"] = datetime.now().isoformat()
                quote["cached"] = False
                quote["data_source"] = "finnhub"
                try:
                    QUOTE_FETCH_COUNTER.labels(
                        ticker=ticker, source="finnhub", status="success"
                    ).inc()
                except Exception:
                    pass

        # If Finnhub also fails, try Alpha Vantage as last resort
        if not quote and _finnhub_consecutive_failures >= 3:
            logger.info(
                f"Finnhub has failed {_finnhub_consecutive_failures} times, trying Alpha Vantage"
            )
            with QUOTE_FETCH_DURATION.labels(
                ticker=ticker, source="alpha_vantage"
            ).time():
                quote = StockPriceService._fetch_from_alpha_vantage(ticker)

            if quote:
                # Add staleness metadata for Alpha Vantage data
                quote["is_stale"] = False
                quote["data_age_seconds"] = 0
                quote["last_updated"] = datetime.now().isoformat()
                quote["cached"] = False
                quote["data_source"] = "alpha_vantage"
                try:
                    QUOTE_FETCH_COUNTER.labels(
                        ticker=ticker, source="alpha_vantage", status="success"
                    ).inc()
                except Exception:
                    pass

        # If both APIs failed, check for stale cache
        if not quote and ticker in _quote_cache:
            logger.warning(f"All live APIs failed for {ticker}, returning stale cache")
            cached_data, cached_time = _quote_cache[ticker]
            age_seconds = int(time.time() - cached_time)

            # Add staleness metadata for stale cache
            cached_data["is_stale"] = True
            cached_data["data_age_seconds"] = age_seconds
            cached_data["last_updated"] = datetime.fromtimestamp(
                cached_time
            ).isoformat()
            cached_data["cached"] = True
            cached_data["data_source"] = "stale_cache"
            cached_data["source_status"] = "stale"

            return cached_data

        # Cache the result if we got data
        if quote:
            # store in in-memory cache (Redis removed)
            _quote_cache[ticker] = (quote, time.time())

        return quote

    @staticmethod
    def get_multiple_quotes(tickers: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get quotes for multiple tickers efficiently using parallel processing.

        Uses ThreadPoolExecutor to fetch multiple quotes concurrently while
        respecting rate limits through the rate limiting in get_stock_quote.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dict mapping ticker to quote data
        """
        results = {}
        tickers_to_fetch: List[str] = []

        # Check in-memory cache (Redis removed)
        for ticker in tickers:
            if ticker in _quote_cache:
                cached_data, cached_time = _quote_cache[ticker]
                age_seconds = int(time.time() - cached_time)
                if age_seconds < _cache_ttl:
                    cached_data["is_stale"] = age_seconds > 60
                    cached_data["data_age_seconds"] = age_seconds
                    cached_data["last_updated"] = datetime.fromtimestamp(
                        cached_time
                    ).isoformat()
                    cached_data["cached"] = True
                    results[ticker] = cached_data
                    continue
            tickers_to_fetch.append(ticker)

        logger.info(
            f"Cache hit: {len(results)}/{len(tickers)}, fetching: {len(tickers_to_fetch)}"
        )

        # Fetch remaining tickers in parallel
        if tickers_to_fetch:
            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ticker = {
                    executor.submit(StockPriceService.get_stock_quote, ticker): ticker
                    for ticker in tickers_to_fetch
                }

                for future in future_to_ticker:
                    ticker = future_to_ticker[future]
                    try:
                        quote = future.result()
                        results[ticker] = quote
                        # In-memory caching is handled in get_stock_quote

                    except Exception as e:
                        logger.error(f"Error getting quote for {ticker}: {e}")
                        results[ticker] = None

        return results

    @staticmethod
    async def get_quotes_for_active_companies(
        db: AsyncSession, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get live quotes for companies with recent insider trading activity.

        Queries database for companies with recent trades and fetches live stock prices.

        Args:
            db: Database session
            limit: Number of companies to fetch (None = all companies)

        Returns:
            List of company data with live prices
        """
        try:
            # Query database for companies with recent trades
            from sqlalchemy import func
            from app.models import Trade

            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            # Build query for companies with recent insider trades
            query = (
                select(Company)
                .join(Trade)
                .where(Trade.transaction_date >= thirty_days_ago)
                .group_by(Company.id)
                .order_by(func.count(Trade.id).desc())
            )

            # Apply limit only if specified
            if limit is not None:
                query = query.limit(limit)

            result = await db.execute(query)
            companies = result.scalars().all()

            if not companies:
                # Fallback: Get any companies from database
                logger.info("No companies with recent trades, fetching any companies")
                query = select(Company).order_by(Company.ticker)

                if limit is not None:
                    query = query.limit(limit)

                result = await db.execute(query)
                companies = result.scalars().all()

            logger.info(f"Fetching market overview for {len(companies)} companies")

            # Get all tickers
            tickers = [company.ticker for company in companies]

            # Create a map of ticker to company name
            ticker_to_name = {company.ticker: company.name for company in companies}

            # Get quotes for all companies using parallel processing
            quotes_dict = StockPriceService.get_multiple_quotes(tickers)

            # Add company names and filter out None results
            results = []
            for ticker, quote in quotes_dict.items():
                if quote:
                    quote["company_name"] = ticker_to_name.get(ticker)
                    results.append(quote)

            logger.info(
                f"Successfully fetched {len(results)}/{len(companies)} live quotes"
            )
            return results

        except Exception as e:
            logger.error(f"Error getting quotes for active companies: {e}")
            return []

    @staticmethod
    def get_price_history(
        ticker: str, days: int = 30
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical price data for a ticker.

        Currently only supports Yahoo Finance. Alpha Vantage could be added
        as fallback but requires different API calls.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of history

        Returns:
            List of price data points or None if failed
        """
        # Check cache first
        cache_key = f"{ticker}_{days}"
        cached_data = StockPriceService._price_history_cache.get(cache_key)
        if cached_data:
            cached_history, cache_time = cached_data
            current_time = time.time()
            if (current_time - cache_time) < StockPriceService._price_history_cache_ttl:
                logger.debug(f"Using cached price history for {ticker} ({days} days)")
                return cached_history
        
        try:
            StockPriceService._rate_limit_yahoo()

            # Use Ticker without custom session - yfinance handles this internally
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days}d")

            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return None

            # Convert to list of dicts
            history = []
            for date, row in hist.iterrows():
                history.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(row["Open"], 2),
                        "high": round(row["High"], 2),
                        "low": round(row["Low"], 2),
                        "close": round(row["Close"], 2),
                        "volume": int(row["Volume"]),
                    }
                )

            logger.info(f"Fetched {len(history)} days of history for {ticker}")
            
            # Cache the results
            StockPriceService._price_history_cache[cache_key] = (history, time.time())
            
            return history

        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {e}")
            return None
