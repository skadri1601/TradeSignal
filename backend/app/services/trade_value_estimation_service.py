"""
Trade Value Estimation Service

Solves the problem of undisclosed trade values by using intelligent estimation:
1. Uses historical price data when available
2. Estimates from similar trades
3. Uses market cap and insider role for context
4. Provides confidence scores for estimates
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models import Trade
from app.services.stock_price_service import StockPriceService

logger = logging.getLogger(__name__)


class TradeValueEstimationService:
    # Class-level cache for price history to avoid repeated fetches across all instances
    _price_history_cache: Dict[str, Tuple[List[Dict], datetime]] = {}
    _cache_ttl = timedelta(minutes=10)  # Cache for 10 minutes
    """
    Service for estimating missing trade values.

    When SEC filings don't disclose total_value or price_per_share,
    this service provides intelligent estimates using:
    - Historical price data
    - Similar trades from same insider/company
    - Market cap context
    - Insider role patterns
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def estimate_missing_trade_value(self, trade: Trade) -> Dict[str, Any]:
        """
        Estimate missing trade value using multiple methods.

        Returns:
            Dict with estimated values and confidence scores
        """
        # If we already have total_value, return it
        if trade.total_value and trade.total_value > 0:
            return {
                "total_value": float(trade.total_value),
                "price_per_share": float(trade.price_per_share)
                if trade.price_per_share
                else None,
                "is_estimated": False,
                "confidence": 1.0,
                "estimation_method": "disclosed",
            }

        # If we have price_per_share but not total_value, calculate it
        if trade.price_per_share and trade.shares:
            estimated_value = float(trade.price_per_share * trade.shares)
            return {
                "total_value": estimated_value,
                "price_per_share": float(trade.price_per_share),
                "is_estimated": False,
                "confidence": 0.95,
                "estimation_method": "calculated_from_price",
            }

        # If we have shares but no price, estimate price
        if trade.shares and not trade.price_per_share:
            estimated_price = await self._estimate_price_per_share(trade)
            if estimated_price:
                estimated_value = float(trade.shares * Decimal(str(estimated_price)))
                return {
                    "total_value": estimated_value,
                    "price_per_share": estimated_price,
                    "is_estimated": True,
                    "confidence": 0.7,
                    "estimation_method": "estimated_price",
                }

        # If we have neither, use historical patterns
        estimated_value = await self._estimate_from_patterns(trade)
        if estimated_value:
            estimated_price = (
                estimated_value / float(trade.shares) if trade.shares else None
            )
            return {
                "total_value": estimated_value,
                "price_per_share": estimated_price,
                "is_estimated": True,
                "confidence": 0.5,
                "estimation_method": "pattern_based",
            }

        # Last resort: use company market cap context
        estimated_value = await self._estimate_from_market_context(trade)
        return {
            "total_value": estimated_value,
            "price_per_share": estimated_value / float(trade.shares)
            if trade.shares
            else None,
            "is_estimated": True,
            "confidence": 0.3,
            "estimation_method": "market_context",
        }

    async def _estimate_price_per_share(self, trade: Trade) -> Optional[float]:
        """Estimate price per share using multiple methods."""
        # Method 1: Get stock price on transaction date
        if trade.company and trade.transaction_date:
            try:
                ticker = trade.company.ticker
                transaction_date = trade.transaction_date

                # Check cache first (class-level cache)
                cache_key = f"{ticker}_history"
                cached_data = TradeValueEstimationService._price_history_cache.get(
                    cache_key
                )

                history = None
                if cached_data:
                    cached_history, cache_time = cached_data
                    if (
                        datetime.utcnow() - cache_time
                        < TradeValueEstimationService._cache_ttl
                    ):
                        history = cached_history
                        logger.debug(f"Using cached price history for {ticker}")

                # Fetch if not cached
                if not history:
                    history = StockPriceService.get_price_history(ticker, days=30)
                    if history:
                        # Update cache (class-level)
                        TradeValueEstimationService._price_history_cache[cache_key] = (
                            history,
                            datetime.utcnow(),
                        )
                        logger.debug(f"Cached price history for {ticker}")

                if history:
                    # Find closest date to transaction
                    closest_price = None
                    min_diff = float("inf")

                    for point in history:
                        try:
                            point_date = datetime.fromisoformat(
                                point["date"].replace("Z", "+00:00")
                            ).date()
                        except Exception:
                            # Try alternative date format
                            try:
                                point_date = datetime.strptime(
                                    point["date"], "%Y-%m-%d"
                                ).date()
                            except Exception:
                                continue
                        diff = abs((point_date - transaction_date).days)
                        if diff < min_diff:
                            min_diff = diff
                            closest_price = point["close"]

                    if closest_price and min_diff <= 5:  # Within 5 days
                        return float(closest_price)
            except Exception as e:
                logger.debug(f"Could not get historical price: {e}")

        # Method 2: Use average price from similar trades
        if trade.company_id and trade.insider_id:
            similar_trades = await self._get_similar_trades(trade)
            if similar_trades:
                prices = [
                    float(t.price_per_share)
                    for t in similar_trades
                    if t.price_per_share and t.price_per_share > 0
                ]
                if prices:
                    return sum(prices) / len(prices)

        # Method 3: Use current stock price as fallback
        if trade.company:
            try:
                quote = StockPriceService.get_stock_quote(trade.company.ticker)
                if quote and quote.get("current_price"):
                    return float(quote["current_price"])
            except Exception as e:
                logger.debug(f"Could not get current price: {e}")

        return None

    async def _get_similar_trades(
        self, trade: Trade, days_back: int = 90
    ) -> list[Trade]:
        """Get similar trades from same insider/company for pattern matching."""
        cutoff_date = trade.transaction_date - timedelta(days=days_back)

        result = await self.db.execute(
            select(Trade)
            .where(
                and_(
                    Trade.company_id == trade.company_id,
                    Trade.insider_id == trade.insider_id,
                    Trade.transaction_date >= cutoff_date,
                    Trade.transaction_date < trade.transaction_date,
                    Trade.transaction_type == trade.transaction_type,
                    Trade.price_per_share.isnot(None),
                    Trade.price_per_share > 0,
                )
            )
            .order_by(Trade.transaction_date.desc())
            .limit(10)
        )
        return result.scalars().all()

    async def _estimate_from_patterns(self, trade: Trade) -> Optional[float]:
        """Estimate value from historical trading patterns."""
        # Get average trade value for this insider/company combination
        if trade.company_id and trade.insider_id:
            result = await self.db.execute(
                select(
                    func.avg(Trade.total_value).label("avg_value"),
                    func.avg(Trade.price_per_share).label("avg_price"),
                ).where(
                    and_(
                        Trade.company_id == trade.company_id,
                        Trade.insider_id == trade.insider_id,
                        Trade.total_value.isnot(None),
                        Trade.total_value > 0,
                    )
                )
            )
            stats = result.first()

            if stats and stats.avg_value:
                return float(stats.avg_value)

            # If no total_value, calculate from avg_price * shares
            if stats and stats.avg_price and trade.shares:
                return float(stats.avg_price * trade.shares)

        return None

    async def _estimate_from_market_context(self, trade: Trade) -> float:
        """Last resort estimation using market cap and insider role."""
        if not trade.company or not trade.shares:
            return 0.0

        # Get current stock price
        try:
            quote = StockPriceService.get_stock_quote(trade.company.ticker)
            if quote and quote.get("current_price"):
                price = float(quote["current_price"])
                return float(trade.shares * Decimal(str(price)))
        except Exception:
            pass

        # Fallback: use $50/share as default (rough market average)
        return float(trade.shares * Decimal("50.0"))

    async def enrich_trade_with_estimates(self, trade: Trade) -> Trade:
        """
        Enrich a trade with estimated values if missing.

        Updates the trade object in-place with estimated values.
        """
        if trade.total_value and trade.total_value > 0:
            return trade  # Already has value

        estimates = await self.estimate_missing_trade_value(trade)

        # Update trade with estimates (don't save to DB, just for display)
        if not trade.total_value or trade.total_value == 0:
            trade.total_value = Decimal(str(estimates["total_value"]))

        if not trade.price_per_share and estimates.get("price_per_share"):
            trade.price_per_share = Decimal(str(estimates["price_per_share"]))

        # Store estimation metadata (could add to a separate field)
        trade._estimation_metadata = {
            "is_estimated": estimates["is_estimated"],
            "confidence": estimates["confidence"],
            "method": estimates["estimation_method"],
        }

        return trade

    async def enrich_trades_batch(self, trades: list[Trade]) -> list[Trade]:
        """Enrich multiple trades with estimates."""
        enriched = []
        for trade in trades:
            enriched_trade = await self.enrich_trade_with_estimates(trade)
            enriched.append(enriched_trade)
        return enriched
