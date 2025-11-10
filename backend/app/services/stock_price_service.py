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
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Company
from app.config import settings
from alpha_vantage.timeseries import TimeSeries

logger = logging.getLogger(__name__)

# Rate limiting
_last_yahoo_request_time = 0
_last_alpha_vantage_request_time = 0
_min_yahoo_interval = 0.2  # 0.2 seconds between Yahoo requests to avoid rate limits
_min_alpha_vantage_interval = 12.0  # 12 seconds between Alpha Vantage requests (5 per minute limit)

# Cache for stock quotes (ticker -> (quote_data, timestamp))
_quote_cache: Dict[str, tuple[Dict[str, Any], float]] = {}
_cache_ttl = 10  # Cache quotes for 10 seconds (allows 15s auto-refresh to get fresh data)

# Track consecutive failures to switch data sources
_yahoo_consecutive_failures = 0
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
                previous_close = float(info.previous_close) if hasattr(info, 'previous_close') else current_price

                price_change = current_price - previous_close
                price_change_percent = (price_change / previous_close) * 100 if previous_close else 0

                # Get market cap and convert to integer
                market_cap = getattr(info, 'market_cap', None)
                if market_cap is not None:
                    market_cap = int(float(market_cap))

                # Get volume and convert to integer
                volume = getattr(info, 'last_volume', None)
                if volume is not None:
                    volume = int(float(volume))

                quote_data = {
                    'ticker': ticker,
                    'current_price': round(current_price, 2),
                    'previous_close': round(previous_close, 2),
                    'price_change': round(price_change, 2),
                    'price_change_percent': round(price_change_percent, 2),
                    'market_cap': market_cap,
                    'volume': volume,
                    'avg_volume': None,
                    'day_high': getattr(info, 'day_high', None),
                    'day_low': getattr(info, 'day_low', None),
                    'fifty_two_week_high': getattr(info, 'year_high', None),
                    'fifty_two_week_low': getattr(info, 'year_low', None),
                    'market_state': 'REGULAR',
                    'updated_at': datetime.utcnow().isoformat()
                }

                # Reset failure counter on success
                _yahoo_consecutive_failures = 0
                logger.info(f"Successfully fetched {ticker} from Yahoo Finance (fast_info)")
                return quote_data

            except Exception as fast_info_error:
                logger.debug(f"fast_info failed for {ticker}, trying history: {fast_info_error}")

                # Fallback to historical data method
                hist = stock.history(period="5d")

                if hist.empty:
                    logger.warning(f"No historical data returned for {ticker}")
                    raise ValueError("Empty history data")

                # Get most recent data
                latest = hist.iloc[-1]
                current_price = float(latest['Close'])

                # Calculate previous close and changes
                if len(hist) > 1:
                    previous = hist.iloc[-2]
                    previous_close = float(previous['Close'])
                else:
                    previous_close = float(latest['Open'])

                price_change = current_price - previous_close
                price_change_percent = (price_change / previous_close) * 100 if previous_close else 0

                # Try to get additional info
                market_cap = None
                try:
                    info_dict = stock.info
                    market_cap = info_dict.get('marketCap')
                    if market_cap is not None:
                        market_cap = int(float(market_cap))
                except:
                    pass

                quote_data = {
                    'ticker': ticker,
                    'current_price': round(current_price, 2),
                    'previous_close': round(previous_close, 2),
                    'price_change': round(price_change, 2),
                    'price_change_percent': round(price_change_percent, 2),
                    'market_cap': market_cap,
                    'volume': int(latest['Volume']) if 'Volume' in latest else None,
                    'avg_volume': None,
                    'day_high': round(float(latest['High']), 2) if 'High' in latest else None,
                    'day_low': round(float(latest['Low']), 2) if 'Low' in latest else None,
                    'fifty_two_week_high': None,
                    'fifty_two_week_low': None,
                    'market_state': 'REGULAR',
                    'updated_at': datetime.utcnow().isoformat()
                }

                # Reset failure counter on success
                _yahoo_consecutive_failures = 0
                logger.info(f"Successfully fetched {ticker} from Yahoo Finance (history)")
                return quote_data

        except Exception as e:
            _yahoo_consecutive_failures += 1
            logger.error(f"Yahoo Finance failed for {ticker} (failure #{_yahoo_consecutive_failures}): {e}")
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
            ts = TimeSeries(key=settings.alpha_vantage_api_key, output_format='json')

            # Get quote data
            data, meta_data = ts.get_quote_endpoint(symbol=ticker)

            if not data or '01. symbol' not in data:
                logger.warning(f"Invalid response from Alpha Vantage for {ticker}")
                return None

            current_price = float(data['05. price'])
            previous_close = float(data['08. previous close'])
            price_change = float(data['09. change'])
            price_change_percent = float(data['10. change percent'].rstrip('%'))

            quote_data = {
                'ticker': ticker,
                'current_price': round(current_price, 2),
                'previous_close': round(previous_close, 2),
                'price_change': round(price_change, 2),
                'price_change_percent': round(price_change_percent, 2),
                'market_cap': None,  # Not available in quote endpoint
                'volume': int(data['06. volume']) if '06. volume' in data else None,
                'avg_volume': None,
                'day_high': round(float(data['03. high']), 2) if '03. high' in data else None,
                'day_low': round(float(data['04. low']), 2) if '04. low' in data else None,
                'fifty_two_week_high': round(float(data['52. week high']), 2) if '52. week high' in data else None,
                'fifty_two_week_low': round(float(data['52. week low']), 2) if '52. week low' in data else None,
                'market_state': 'REGULAR',
                'updated_at': datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully fetched {ticker} from Alpha Vantage")
            return quote_data

        except Exception as e:
            logger.error(f"Alpha Vantage failed for {ticker}: {e}")
            return None

    @staticmethod
    def get_stock_quote(ticker: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
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
            Dict with price data or None if all sources failed
        """
        # Check cache first - SKIP rate limiting for cached data
        if use_cache and ticker in _quote_cache:
            cached_data, cached_time = _quote_cache[ticker]
            age = time.time() - cached_time
            if age < _cache_ttl:
                logger.debug(f"Using cached data for {ticker} (age: {age:.1f}s)")
                return cached_data

        # Try Yahoo Finance first
        quote = StockPriceService._fetch_from_yahoo(ticker)

        # If Yahoo fails repeatedly, try Alpha Vantage
        if not quote and _yahoo_consecutive_failures >= _max_yahoo_failures_before_fallback:
            logger.info(f"Yahoo Finance has failed {_yahoo_consecutive_failures} times, trying Alpha Vantage")
            quote = StockPriceService._fetch_from_alpha_vantage(ticker)

        # If both APIs failed, check for stale cache
        if not quote and ticker in _quote_cache:
            logger.warning(f"All live APIs failed for {ticker}, returning stale cache")
            cached_data, _ = _quote_cache[ticker]
            return cached_data

        # Cache the result if we got data
        if quote:
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

        # Use ThreadPoolExecutor for parallel fetching
        # Limit to 10 concurrent threads to avoid overwhelming the API
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(StockPriceService.get_stock_quote, ticker): ticker
                for ticker in tickers
            }

            # Collect results as they complete
            for future in future_to_ticker:
                ticker = future_to_ticker[future]
                try:
                    quote = future.result()
                    results[ticker] = quote
                except Exception as e:
                    logger.error(f"Error getting quote for {ticker}: {e}")
                    results[ticker] = None

        return results

    @staticmethod
    async def get_quotes_for_active_companies(
        db: AsyncSession,
        limit: Optional[int] = None
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
            from datetime import datetime, timedelta
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
                    quote['company_name'] = ticker_to_name.get(ticker)
                    results.append(quote)

            logger.info(f"Successfully fetched {len(results)}/{len(companies)} live quotes")
            return results

        except Exception as e:
            logger.error(f"Error getting quotes for active companies: {e}")
            return []

    @staticmethod
    def get_price_history(ticker: str, days: int = 30) -> Optional[List[Dict[str, Any]]]:
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
                history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })

            logger.info(f"Fetched {len(history)} days of history for {ticker}")
            return history

        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {e}")
            return None
