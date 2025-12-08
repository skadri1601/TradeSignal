"""
Pattern Analysis Service - Stock Prediction AI

Analyzes insider trading patterns to identify trends and make predictions:
- Buying momentum patterns
- Selling pressure patterns
- Insider cluster analysis
- Price correlation analysis
- Stock recommendations
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from app.models import Trade, Company, Insider

logger = logging.getLogger(__name__)


class PatternAnalysisService:
    """
    Service for analyzing insider trading patterns and generating predictions.

    Features:
    - Pattern detection (momentum, reversal, clustering)
    - Trend identification
    - Stock predictions
    - Risk assessment
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_company_patterns(
        self, ticker: str, days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze trading patterns for a specific company.

        Returns:
            Dict with pattern analysis, trends, and predictions
        """
        try:
            # Get company
            try:
                result = await self.db.execute(
                    select(Company).where(Company.ticker == ticker.upper())
                )
                company = result.scalar_one_or_none()
            except Exception as e:
                logger.error(
                    f"Database error fetching company {ticker}: {e}", exc_info=True
                )
                return {"error": "Database connection error. Please try again later."}

            if not company:
                return {"error": f"Company {ticker} not found"}

            # Get trades
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            try:
                result = await self.db.execute(
                    select(Trade, Insider)
                    .join(Insider, Trade.insider_id == Insider.id)
                    .where(
                        and_(
                            Trade.company_id == company.id,
                            Trade.transaction_date >= cutoff_date,
                        )
                    )
                    .order_by(Trade.transaction_date.desc())
                )
                trades_with_insiders = result.all()
            except Exception as e:
                logger.error(
                    f"Database error fetching trades for {ticker}: {e}", exc_info=True
                )
                return {"error": "Database connection error. Please try again later."}

            if not trades_with_insiders:
                return {
                    "ticker": ticker,
                    "company_name": company.name,
                    "pattern": "NO_ACTIVITY",
                    "trend": "NEUTRAL",
                    "prediction": "No recent insider activity",
                    "confidence": 0.0,
                    "recommendation": "HOLD",
                    "analysis": {},
                }

            # Analyze patterns
            analysis = await self._analyze_patterns(trades_with_insiders, days_back)

            # Generate prediction
            prediction = await self._generate_prediction(analysis, company)

            return {
                "ticker": ticker,
                "company_name": company.name,
                "days_analyzed": days_back,
                "total_trades": len(trades_with_insiders),
                **analysis,
                **prediction,
            }

        except Exception as e:
            logger.error(f"Error analyzing patterns for {ticker}: {e}", exc_info=True)
            return {"error": str(e)}

    async def get_top_patterns(
        self, pattern_type: str = "BUYING_MOMENTUM", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top companies with specific patterns.

        Args:
            pattern_type: BUYING_MOMENTUM, SELLING_PRESSURE, CLUSTER, REVERSAL
            limit: Number of companies to return
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=90)

            # Get companies with recent activity
            try:
                result = await self.db.execute(
                    select(
                        Company.id,
                        Company.ticker,
                        Company.name,
                        func.count(Trade.id).label("trade_count"),
                        func.sum(
                            case(
                                (Trade.transaction_type == "BUY", Trade.total_value),
                                else_=0,
                            )
                        ).label("total_buy_value"),
                        func.sum(
                            case(
                                (Trade.transaction_type == "SELL", Trade.total_value),
                                else_=0,
                            )
                        ).label("total_sell_value"),
                        func.count(func.distinct(Insider.id)).label("insider_count"),
                    )
                    .join(Trade, Company.id == Trade.company_id)
                    .join(Insider, Trade.insider_id == Insider.id)
                    .where(Trade.transaction_date >= cutoff_date)
                    .group_by(Company.id, Company.ticker, Company.name)
                    .having(func.count(Trade.id) >= 3)
                    .order_by(func.count(Trade.id).desc())
                    .limit(limit * 3)  # Get more to filter by pattern
                )
                companies = result.all()
            except Exception as e:
                logger.error(
                    f"Database error fetching companies for pattern {pattern_type}: {e}",
                    exc_info=True,
                )
                raise Exception("Database connection error. Please try again later.")

            # Analyze each company
            patterns = []
            for company_row in companies:
                (
                    company_id,
                    ticker,
                    name,
                    trade_count,
                    buy_value,
                    sell_value,
                    insider_count,
                ) = company_row

                # Get detailed trades
                try:
                    result = await self.db.execute(
                        select(Trade, Insider)
                        .join(Insider, Trade.insider_id == Insider.id)
                        .where(
                            and_(
                                Trade.company_id == company_id,
                                Trade.transaction_date >= cutoff_date,
                            )
                        )
                        .order_by(Trade.transaction_date.desc())
                    )
                    trades = result.all()
                except Exception as e:
                    logger.error(
                        f"Database error fetching trades for {ticker}: {e}",
                        exc_info=True,
                    )
                    continue  # Skip this company and continue with next

                if not trades:
                    continue

                # Analyze pattern
                try:
                    analysis = await self._analyze_patterns(trades, 90)
                except Exception as e:
                    logger.error(
                        f"Error analyzing patterns for {ticker}: {e}", exc_info=True
                    )
                    continue  # Skip this company and continue with next

                # Check if matches requested pattern
                if (
                    pattern_type == "BUYING_MOMENTUM"
                    and analysis.get("pattern") == "BUYING_MOMENTUM"
                ):
                    patterns.append(
                        {
                            "ticker": ticker,
                            "company_name": name,
                            "pattern": analysis["pattern"],
                            "trend": analysis["trend"],
                            "confidence": analysis["confidence"],
                            "trade_count": trade_count,
                            "insider_count": insider_count,
                            "buy_value": float(buy_value or 0),
                            "sell_value": float(sell_value or 0),
                            **analysis,
                        }
                    )
                elif (
                    pattern_type == "SELLING_PRESSURE"
                    and analysis.get("pattern") == "SELLING_PRESSURE"
                ):
                    patterns.append(
                        {
                            "ticker": ticker,
                            "company_name": name,
                            "pattern": analysis["pattern"],
                            "trend": analysis["trend"],
                            "confidence": analysis["confidence"],
                            "trade_count": trade_count,
                            "insider_count": insider_count,
                            "buy_value": float(buy_value or 0),
                            "sell_value": float(sell_value or 0),
                            **analysis,
                        }
                    )
                elif pattern_type == "CLUSTER" and analysis.get("pattern") == "CLUSTER":
                    patterns.append(
                        {
                            "ticker": ticker,
                            "company_name": name,
                            "pattern": analysis["pattern"],
                            "trend": analysis["trend"],
                            "confidence": analysis["confidence"],
                            "trade_count": trade_count,
                            "insider_count": insider_count,
                            "buy_value": float(buy_value or 0),
                            "sell_value": float(sell_value or 0),
                            **analysis,
                        }
                    )
                elif (
                    pattern_type == "REVERSAL" and analysis.get("pattern") == "REVERSAL"
                ):
                    patterns.append(
                        {
                            "ticker": ticker,
                            "company_name": name,
                            "pattern": analysis["pattern"],
                            "trend": analysis["trend"],
                            "confidence": analysis["confidence"],
                            "trade_count": trade_count,
                            "insider_count": insider_count,
                            "buy_value": float(buy_value or 0),
                            "sell_value": float(sell_value or 0),
                            **analysis,
                        }
                    )

                if len(patterns) >= limit:
                    break

            # Sort by confidence
            patterns.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            return patterns[:limit]
        except Exception as e:
            logger.error(
                f"Error in get_top_patterns for {pattern_type}: {e}", exc_info=True
            )
            error_str = str(e).lower()
            if (
                "connection" in error_str
                or "database" in error_str
                or "pool" in error_str
            ):
                raise Exception("Database connection error. Please try again later.")
            raise

    async def _analyze_patterns(
        self, trades_with_insiders: List[tuple], days_back: int
    ) -> Dict[str, Any]:
        """Analyze trading patterns from trade data."""
        if not trades_with_insiders:
            return {
                "pattern": "NO_ACTIVITY",
                "trend": "NEUTRAL",
                "confidence": 0.0,
                "analysis": {},
            }

        # Separate buys and sells
        buys = []
        sells = []
        insider_activity = {}  # Track activity by insider

        # Import value estimation service
        from app.services.trade_value_estimation_service import (
            TradeValueEstimationService,
        )

        value_service = TradeValueEstimationService(self.db)

        for trade, insider in trades_with_insiders:
            # Use value estimation service for missing values
            if not trade.total_value or trade.total_value == 0:
                estimates = await value_service.estimate_missing_trade_value(trade)
                trade_value = estimates.get("total_value", 0)
            else:
                trade_value = float(trade.total_value)

            # Fallback calculation if still 0
            if trade_value == 0 and trade.price_per_share and trade.shares:
                trade_value = float(trade.price_per_share * trade.shares)

            # Ensure trade_value is never NaN or None
            if not isinstance(trade_value, (int, float)) or (
                isinstance(trade_value, float)
                and (
                    trade_value != trade_value
                    or trade_value == float("inf")
                    or trade_value == float("-inf")
                )
            ):
                trade_value = 0.0

            # Ensure shares is valid
            shares_value = float(trade.shares) if trade.shares else 0.0
            if not isinstance(shares_value, (int, float)) or (
                isinstance(shares_value, float)
                and (
                    shares_value != shares_value
                    or shares_value == float("inf")
                    or shares_value == float("-inf")
                )
            ):
                shares_value = 0.0

            trade_data = {
                "date": trade.transaction_date,
                "value": trade_value,
                "shares": shares_value,
                "insider": insider.name,
                "role": insider.title or insider.relationship or "Insider",
            }

            if trade.transaction_type == "BUY":
                buys.append(trade_data)
            else:
                sells.append(trade_data)

            # Track insider activity
            if insider.name not in insider_activity:
                insider_activity[insider.name] = {
                    "buys": 0,
                    "sells": 0,
                    "total_value": 0,
                }

            if trade.transaction_type == "BUY":
                insider_activity[insider.name]["buys"] += 1
            else:
                insider_activity[insider.name]["sells"] += 1
            insider_activity[insider.name]["total_value"] += trade_value

        # Calculate metrics with NaN protection
        total_buy_value = sum(
            b["value"]
            for b in buys
            if isinstance(b.get("value"), (int, float)) and b["value"] == b["value"]
        )
        total_sell_value = sum(
            s["value"]
            for s in sells
            if isinstance(s.get("value"), (int, float)) and s["value"] == s["value"]
        )

        # Ensure values are never NaN
        if not isinstance(total_buy_value, (int, float)) or (
            isinstance(total_buy_value, float)
            and (
                total_buy_value != total_buy_value
                or total_buy_value == float("inf")
                or total_buy_value == float("-inf")
            )
        ):
            total_buy_value = 0.0
        if not isinstance(total_sell_value, (int, float)) or (
            isinstance(total_sell_value, float)
            and (
                total_sell_value != total_sell_value
                or total_sell_value == float("inf")
                or total_sell_value == float("-inf")
            )
        ):
            total_sell_value = 0.0

        total_value = total_buy_value + total_sell_value

        # Calculate ratios and cap at 1.0 (100%)
        buy_ratio = min(1.0, total_buy_value / total_value) if total_value > 0 else 0.0
        sell_ratio = (
            min(1.0, total_sell_value / total_value) if total_value > 0 else 0.0
        )

        # Ensure ratios are never NaN
        if not isinstance(buy_ratio, (int, float)) or (
            isinstance(buy_ratio, float) and buy_ratio != buy_ratio
        ):
            buy_ratio = 0.0
        if not isinstance(sell_ratio, (int, float)) or (
            isinstance(sell_ratio, float) and sell_ratio != sell_ratio
        ):
            sell_ratio = 0.0

        # Detect patterns
        pattern = "NEUTRAL"
        trend = "NEUTRAL"
        confidence = 0.5

        # Pattern 1: Buying Momentum
        if buy_ratio > 0.7 and len(buys) >= 3:
            # Check if recent buys are increasing
            recent_buys = sorted(buys, key=lambda x: x["date"], reverse=True)[:5]
            if len(recent_buys) >= 3:
                values = [b["value"] for b in recent_buys]
                if values[0] > values[-1]:  # Increasing trend
                    pattern = "BUYING_MOMENTUM"
                    trend = "BULLISH"
                    confidence = min(0.9, 0.6 + (buy_ratio - 0.7) * 0.5)

        # Pattern 2: Selling Pressure
        elif sell_ratio > 0.7 and len(sells) >= 3:
            # Check if recent sells are increasing
            recent_sells = sorted(sells, key=lambda x: x["date"], reverse=True)[:5]
            if len(recent_sells) >= 3:
                values = [s["value"] for s in recent_sells]
                if values[0] > values[-1]:  # Increasing trend
                    pattern = "SELLING_PRESSURE"
                    trend = "BEARISH"
                    confidence = min(0.9, 0.6 + (sell_ratio - 0.7) * 0.5)

        # Pattern 3: Cluster (multiple insiders trading together)
        active_insiders = len(
            [i for i in insider_activity.values() if i["total_value"] > 0]
        )
        if active_insiders >= 3 and len(trades_with_insiders) >= 5:
            # Check if trades are clustered in time
            dates = sorted([t[0].transaction_date for t in trades_with_insiders])
            if len(dates) >= 3:
                time_span = (dates[-1] - dates[0]).days
                if time_span <= 30:  # Clustered within 30 days
                    if buy_ratio > 0.6:
                        pattern = "CLUSTER"
                        trend = "BULLISH"
                        confidence = 0.75
                    elif sell_ratio > 0.6:
                        pattern = "CLUSTER"
                        trend = "BEARISH"
                        confidence = 0.75

        # Pattern 4: Reversal (pattern change)
        if len(buys) >= 2 and len(sells) >= 2:
            # Check if recent activity reversed
            recent_trades = sorted(
                trades_with_insiders, key=lambda x: x[0].transaction_date, reverse=True
            )[:6]

            recent_types = [t[0].transaction_type for t in recent_trades]
            if len(recent_types) >= 4:
                first_half = recent_types[: len(recent_types) // 2]
                second_half = recent_types[len(recent_types) // 2 :]

                first_buy_ratio = first_half.count("BUY") / len(first_half)
                second_buy_ratio = second_half.count("BUY") / len(second_half)

                if abs(first_buy_ratio - second_buy_ratio) > 0.4:
                    pattern = "REVERSAL"
                    if second_buy_ratio > first_buy_ratio:
                        trend = "BULLISH"
                    else:
                        trend = "BEARISH"
                    confidence = 0.7

        # Ensure all return values are valid numbers
        safe_total_buy_value = (
            float(total_buy_value)
            if isinstance(total_buy_value, (int, float))
            and total_buy_value == total_buy_value
            else 0.0
        )
        safe_total_sell_value = (
            float(total_sell_value)
            if isinstance(total_sell_value, (int, float))
            and total_sell_value == total_sell_value
            else 0.0
        )

        return {
            "pattern": pattern,
            "trend": trend,
            "confidence": round(confidence, 2),
            "buy_ratio": round(
                min(1.0, max(0.0, buy_ratio)), 4
            ),  # Cap between 0 and 1, round to 4 decimals
            "sell_ratio": round(
                min(1.0, max(0.0, sell_ratio)), 4
            ),  # Cap between 0 and 1, round to 4 decimals
            "total_buy_value": safe_total_buy_value,
            "total_sell_value": safe_total_sell_value,
            "active_insiders": active_insiders,
            "analysis": {
                "buy_count": len(buys),
                "sell_count": len(sells),
                "insider_activity": insider_activity,
            },
        }

    async def _generate_prediction(
        self, analysis: Dict[str, Any], company: Company
    ) -> Dict[str, Any]:
        """Generate stock prediction based on pattern analysis using Gemini AI."""
        pattern = analysis.get("pattern", "NEUTRAL")
        trend = analysis.get("trend", "NEUTRAL")
        confidence = analysis.get("confidence", 0.5)
        buy_ratio = analysis.get("buy_ratio", 0.0)
        sell_ratio = analysis.get("sell_ratio", 0.0)
        total_buy_value = analysis.get("total_buy_value", 0.0)
        total_sell_value = analysis.get("total_sell_value", 0.0)
        active_insiders = analysis.get("active_insiders", 0)
        buy_count = analysis.get("analysis", {}).get("buy_count", 0)
        sell_count = analysis.get("analysis", {}).get("sell_count", 0)

        # Try to use Gemini AI for enhanced prediction
        try:
            from app.config import settings as gemini_settings

            if gemini_settings.gemini_api_key and gemini_settings.enable_ai_insights:
                import google.generativeai as genai

                genai.configure(api_key=gemini_settings.gemini_api_key)
                model_name = gemini_settings.gemini_model
                if model_name and not model_name.startswith("models/"):
                    model_name = f"models/{model_name}"
                model = genai.GenerativeModel(model_name)

                prompt = f"""You are a senior financial analyst specializing in insider trading pattern analysis.

Analyze the following insider trading pattern for {company.name} ({company.ticker}):

Pattern Type: {pattern}
Trend: {trend}
Confidence: {confidence:.1%}
Buy Ratio: {buy_ratio:.1%} ({buy_count} buy trades, ${total_buy_value:,.0f} total)
Sell Ratio: {sell_ratio:.1%} ({sell_count} sell trades, \
${total_sell_value:,.0f} total)
Active Insiders: {active_insiders}

Provide a concise but insightful prediction (2-3 sentences) explaining what \
this pattern means for the stock's future performance. Be specific about the \
implications and what investors should watch for.

Respond with ONLY the prediction text, no additional formatting."""

                response = await model.generate_content_async(prompt)
                ai_prediction = response.text.strip()

                # Use AI prediction if available
                prediction = ai_prediction
            else:
                raise ValueError("Gemini not configured")
        except Exception as e:
            logger.debug(
                f"Gemini AI not available for pattern prediction: {e}, using fallback"
            )
            # Fallback to static predictions
            predictions = {
                "BUYING_MOMENTUM": (
                    f"Strong insider buying momentum detected for {company.ticker}. "
                    f"{buy_count} buy transactions totaling ${total_buy_value:,.0f} "
                    "suggest insiders have positive conviction. Multiple insiders "
                    f"({active_insiders}) are accumulating shares, indicating "
                    "potential upside."
                ),
                "SELLING_PRESSURE": (
                    f"Significant insider selling pressure detected for {company.ticker}. "
                    f"{sell_count} sell transactions totaling ${total_sell_value:,.0f} "
                    "suggest insiders are reducing positions. This may indicate concerns "
                    "about valuation or upcoming challenges."
                ),
                "CLUSTER": (
                    f"Clustered insider activity detected for {company.ticker}. "
                    f"{active_insiders} insiders trading together within a short "
                    "timeframe may indicate significant corporate events, earnings "
                    "announcements, or strategic changes ahead."
                ),
                "REVERSAL": (
                    f"Pattern reversal detected for {company.ticker}. Recent insider "
                    "activity shows a shift from previous trends, suggesting changing "
                    "sentiment among company insiders."
                ),
                "NEUTRAL": (
                    f"Mixed insider activity for {company.ticker}. No clear "
                    f"directional pattern detected. {buy_count} buys and {sell_count} "
                    "sells suggest balanced insider sentiment."
                ),
                "NO_ACTIVITY": f"No recent insider activity for {company.ticker}.",
            }
            prediction = predictions.get(pattern, predictions["NEUTRAL"])

        # Generate recommendation
        if trend == "BULLISH" and confidence > 0.6:
            recommendation = "BUY"
        elif trend == "BEARISH" and confidence > 0.6:
            recommendation = "SELL"
        elif trend == "BULLISH" and confidence > 0.4:
            recommendation = "CONSIDER_BUY"
        elif trend == "BEARISH" and confidence > 0.4:
            recommendation = "CONSIDER_SELL"
        else:
            recommendation = "HOLD"

        return {
            "prediction": prediction,
            "recommendation": recommendation,
            "risk_level": "LOW"
            if confidence < 0.5
            else "MEDIUM"
            if confidence < 0.7
            else "HIGH",
        }
