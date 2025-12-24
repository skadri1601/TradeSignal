"""
Market Data Service

Unified service for fetching market data from multiple sources:
- Technical analysis (price history, indicators)
- Fundamental analysis (financials, ratios)
- Analyst ratings and price targets
- News sentiment analysis
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

# Optional imports with fallbacks
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import ta
    from ta.trend import SMAIndicator, EMAIndicator, MACD
    from ta.momentum import RSIIndicator
    from ta.volatility import BollingerBands
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    """Unified market data service for comprehensive stock analysis."""

    def __init__(self):
        """Initialize market data service with API clients."""
        self.finnhub_client = None

        # Initialize Finnhub client if available and configured
        if FINNHUB_AVAILABLE and settings.finnhub_api_key:
            try:
                self.finnhub_client = finnhub.Client(api_key=settings.finnhub_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Finnhub client: {e}")

    async def get_technical_indicators(
        self, ticker: str, period: str = "1y"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch technical analysis data.

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)

        Returns:
            Dictionary with technical indicators or None if unavailable
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available, skipping technical analysis")
            return None

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                logger.warning(f"No price history available for {ticker}")
                return None

            # Current price data
            current_price = float(hist['Close'].iloc[-1]) if len(hist) > 0 else None
            volume = int(hist['Volume'].iloc[-1]) if len(hist) > 0 else None

            # 52-week high/low
            week_52_high = float(hist['High'].max()) if len(hist) > 0 else None
            week_52_low = float(hist['Low'].min()) if len(hist) > 0 else None

            technical_data = {
                "current_price": current_price,
                "volume": volume,
                "52_week_high": week_52_high,
                "52_week_low": week_52_low,
                "period": period,
            }

            # Calculate technical indicators if TA library available
            if TA_AVAILABLE and len(hist) >= 200:
                try:
                    # Moving averages
                    sma_20 = SMAIndicator(close=hist['Close'], window=20)
                    sma_50 = SMAIndicator(close=hist['Close'], window=50)
                    sma_200 = SMAIndicator(close=hist['Close'], window=200)

                    ema_12 = EMAIndicator(close=hist['Close'], window=12)
                    ema_26 = EMAIndicator(close=hist['Close'], window=26)

                    # RSI
                    rsi = RSIIndicator(close=hist['Close'], window=14)

                    # MACD
                    macd_indicator = MACD(close=hist['Close'])

                    # Bollinger Bands
                    bollinger = BollingerBands(close=hist['Close'])

                    technical_data.update({
                        "sma_20": float(sma_20.sma_indicator().iloc[-1]),
                        "sma_50": float(sma_50.sma_indicator().iloc[-1]),
                        "sma_200": float(sma_200.sma_indicator().iloc[-1]),
                        "ema_12": float(ema_12.ema_indicator().iloc[-1]),
                        "ema_26": float(ema_26.ema_indicator().iloc[-1]),
                        "rsi_14": float(rsi.rsi().iloc[-1]),
                        "macd": {
                            "macd": float(macd_indicator.macd().iloc[-1]),
                            "signal": float(macd_indicator.macd_signal().iloc[-1]),
                            "histogram": float(macd_indicator.macd_diff().iloc[-1]),
                        },
                        "bollinger": {
                            "upper": float(bollinger.bollinger_hband().iloc[-1]),
                            "middle": float(bollinger.bollinger_mavg().iloc[-1]),
                            "lower": float(bollinger.bollinger_lband().iloc[-1]),
                        },
                    })

                    # Determine trend based on price vs SMAs
                    if current_price > technical_data["sma_200"]:
                        trend = "UPTREND"
                    elif current_price < technical_data["sma_200"]:
                        trend = "DOWNTREND"
                    else:
                        trend = "NEUTRAL"

                    technical_data["trend"] = trend

                    # Determine momentum based on RSI
                    rsi_value = technical_data["rsi_14"]
                    if rsi_value > 70:
                        momentum = "OVERBOUGHT"
                    elif rsi_value > 50:
                        momentum = "BULLISH"
                    elif rsi_value > 30:
                        momentum = "BEARISH"
                    else:
                        momentum = "OVERSOLD"

                    technical_data["momentum"] = momentum

                    # Volume trend (compare recent vs average)
                    avg_volume = hist['Volume'].mean()
                    if volume > avg_volume * 1.5:
                        volume_trend = "INCREASING"
                    elif volume < avg_volume * 0.5:
                        volume_trend = "DECREASING"
                    else:
                        volume_trend = "NORMAL"

                    technical_data["volume_trend"] = volume_trend
                    technical_data["avg_volume"] = int(avg_volume)

                except Exception as e:
                    logger.warning(f"Failed to calculate some indicators for {ticker}: {e}")

            return technical_data

        except Exception as e:
            logger.error(f"Failed to fetch technical data for {ticker}: {e}")
            return None

    async def get_fundamental_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch fundamental analysis data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with fundamental metrics or None if unavailable
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available, skipping fundamental analysis")
            return None

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                logger.warning(f"No fundamental data available for {ticker}")
                return None

            fundamental_data = {
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "revenue": info.get("totalRevenue"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "free_cash_flow": info.get("freeCashflow"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52_week_change": info.get("52WeekChange"),
            }

            # Determine valuation based on P/E ratio
            pe = fundamental_data.get("pe_ratio")
            if pe:
                if pe < 15:
                    valuation = "UNDERVALUED"
                elif pe < 25:
                    valuation = "FAIRLY_VALUED"
                elif pe < 40:
                    valuation = "OVERVALUED"
                else:
                    valuation = "HIGHLY_OVERVALUED"
            else:
                valuation = "UNKNOWN"

            fundamental_data["valuation"] = valuation

            # Format large numbers for readability
            market_cap = fundamental_data.get("market_cap")
            if market_cap:
                if market_cap >= 1_000_000_000_000:
                    fundamental_data["market_cap_formatted"] = f"${market_cap/1_000_000_000_000:.2f}T"
                elif market_cap >= 1_000_000_000:
                    fundamental_data["market_cap_formatted"] = f"${market_cap/1_000_000_000:.2f}B"
                elif market_cap >= 1_000_000:
                    fundamental_data["market_cap_formatted"] = f"${market_cap/1_000_000:.2f}M"

            return fundamental_data

        except Exception as e:
            logger.error(f"Failed to fetch fundamental data for {ticker}: {e}")
            return None

    async def get_analyst_ratings(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch analyst ratings and price targets.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with analyst consensus or None if unavailable
        """
        if not self.finnhub_client:
            logger.warning("Finnhub not configured, skipping analyst ratings")
            return None

        try:
            # Get recommendation trends
            recommendations = self.finnhub_client.recommendation_trends(ticker)

            if not recommendations:
                logger.warning(f"No analyst ratings available for {ticker}")
                return None

            # Get most recent recommendations
            latest = recommendations[0] if recommendations else {}

            buy_count = latest.get("buy", 0) + latest.get("strongBuy", 0)
            hold_count = latest.get("hold", 0)
            sell_count = latest.get("sell", 0) + latest.get("strongSell", 0)
            total = buy_count + hold_count + sell_count

            # Determine consensus
            if total == 0:
                consensus = "NO_CONSENSUS"
            elif buy_count / total >= 0.7:
                consensus = "STRONG_BUY"
            elif buy_count / total >= 0.5:
                consensus = "BUY"
            elif sell_count / total >= 0.7:
                consensus = "STRONG_SELL"
            elif sell_count / total >= 0.5:
                consensus = "SELL"
            else:
                consensus = "HOLD"

            analyst_data = {
                "consensus": consensus,
                "buy_count": buy_count,
                "hold_count": hold_count,
                "sell_count": sell_count,
                "analyst_count": total,
                "period": latest.get("period"),
            }

            # Get price targets
            try:
                price_target = self.finnhub_client.price_target(ticker)
                if price_target:
                    analyst_data.update({
                        "avg_price_target": price_target.get("targetMean"),
                        "high_target": price_target.get("targetHigh"),
                        "low_target": price_target.get("targetLow"),
                        "median_target": price_target.get("targetMedian"),
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch price targets for {ticker}: {e}")

            return analyst_data

        except Exception as e:
            logger.error(f"Failed to fetch analyst ratings for {ticker}: {e}")
            return None

    async def get_news_sentiment(
        self, ticker: str, days_back: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch recent news and sentiment.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back

        Returns:
            Dictionary with news and sentiment or None if unavailable
        """
        if not self.finnhub_client:
            logger.warning("Finnhub not configured, skipping news sentiment")
            return None

        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            # Get company news
            news = self.finnhub_client.company_news(
                ticker,
                _from=from_date.strftime("%Y-%m-%d"),
                to=to_date.strftime("%Y-%m-%d"),
            )

            if not news:
                logger.warning(f"No news available for {ticker}")
                return None

            # Process news items
            recent_headlines = []
            sentiment_scores = []

            for item in news[:10]:  # Limit to 10 most recent
                headline = {
                    "title": item.get("headline"),
                    "source": item.get("source"),
                    "url": item.get("url"),
                    "date": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d"),
                }

                # Finnhub doesn't provide sentiment, so we'd need to use another service
                # For now, we'll note it as unavailable
                headline["sentiment"] = None

                recent_headlines.append(headline)

            # Calculate overall sentiment if available
            overall_sentiment = "NEUTRAL"  # Default
            sentiment_score = 0.5  # Default neutral

            return {
                "recent_headlines": recent_headlines,
                "overall_sentiment": overall_sentiment,
                "sentiment_score": sentiment_score,
                "news_count": len(news),
                "days_analyzed": days_back,
            }

        except Exception as e:
            logger.error(f"Failed to fetch news sentiment for {ticker}: {e}")
            return None

    async def get_comprehensive_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get all available market data for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with all available data
        """
        logger.info(f"Fetching comprehensive market data for {ticker}")

        data = {
            "ticker": ticker,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Fetch all data sources in parallel (using asyncio tasks in production)
        if settings.enable_technical_analysis:
            data["technical"] = await self.get_technical_indicators(ticker)

        if settings.enable_fundamental_analysis:
            data["fundamental"] = await self.get_fundamental_data(ticker)

        if settings.enable_analyst_ratings:
            data["analyst"] = await self.get_analyst_ratings(ticker)

        if settings.enable_news_sentiment:
            data["news"] = await self.get_news_sentiment(ticker)

        return data
