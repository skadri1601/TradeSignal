"""
AI Service for TradeSignal.

Provides AI-powered insights using OpenAI's GPT models.
Analyzes insider trading patterns and generates natural language summaries.
"""

import logging
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case

from app.config import settings
from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for AI-powered trade analysis and insights.

    Supports multiple AI providers with automatic fallback:
    - Google Gemini 2.5 Flash (default - cheap, ultra-fast, 1M+ context)
    - OpenAI GPT-4o-mini (fallback - reliable, structured output)

    Features:
    - Analyze company trading patterns
    - Generate daily summaries
    - Answer natural language queries
    - Provide trading signals
    - Price prediction modeling (PRO)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = settings.ai_provider.lower()
        self.gemini_client = None
        self.openai_client = None

        # Initialize Gemini
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                gemini_model_name = settings.gemini_model
                if gemini_model_name and not gemini_model_name.startswith("models/"):
                    gemini_model_name = f"models/{gemini_model_name}"
                self.gemini_client = genai.GenerativeModel(gemini_model_name)
                logger.info(f"Gemini initialized: {gemini_model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

        # Initialize OpenAI
        if settings.openai_api_key:
            try:
                from openai import AsyncOpenAI

                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info(f"OpenAI initialized: {settings.openai_model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")

    def _check_availability(self) -> bool:
        """Check if AI service is available."""
        if not settings.enable_ai_insights:
            logger.warning("AI insights feature is disabled")
            return False

        if self.provider == "gemini" and self.gemini_client:
            return True
        elif self.provider == "openai" and self.openai_client:
            return True
        elif self.gemini_client:
            logger.info("Primary provider unavailable, using Gemini fallback")
            self.provider = "gemini"
            return True
        elif self.openai_client:
            logger.info("Primary provider unavailable, using OpenAI fallback")
            self.provider = "openai"
            return True

        logger.warning("No AI provider configured")
        return False

    def _provider_sequence(self) -> List[str]:
        """Return provider order with fallbacks."""
        sequence: List[str] = []
        primary = self.provider

        if primary == "gemini":
            if self.gemini_client:
                sequence.append("gemini")
            if self.openai_client:
                sequence.append("openai")
        elif primary == "openai":
            if self.openai_client:
                sequence.append("openai")
            if self.gemini_client:
                sequence.append("gemini")
        else:
            if self.gemini_client:
                sequence.append("gemini")
            if self.openai_client:
                sequence.append("openai")

        if not sequence:
            if self.gemini_client:
                sequence.append("gemini")
            if self.openai_client and "openai" not in sequence:
                sequence.append("openai")

        return sequence

    async def analyze_company(
        self, ticker: str, days_back: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze recent insider trading activity for a company.

        Args:
            ticker: Company ticker symbol
            days_back: Number of days to analyze (default: 30)

        Returns:
            Dict with AI analysis or None if unavailable
        """
        if not self._check_availability():
            return None

        try:
            # Get company
            result = await self.db.execute(
                select(Company).where(Company.ticker == ticker.upper())
            )
            company = result.scalar_one_or_none()

            if not company:
                return {"error": f"Company {ticker} not found"}

            # Get recent trades
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            result = await self.db.execute(
                select(Trade, Insider)
                .join(Insider, Trade.insider_id == Insider.id)
                .where(
                    and_(
                        Trade.company_id == company.id, Trade.filing_date >= cutoff_date
                    )
                )
                .order_by(desc(Trade.filing_date))
                .limit(50)
            )
            trades_with_insiders = result.all()

            if not trades_with_insiders:
                return {
                    "ticker": ticker,
                    "company_name": company.name,
                    "analysis": f"No insider trading activity found for {company.name} in the last {days_back} days.",
                    "sentiment": "NEUTRAL",
                    "total_trades": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Prepare trade data for AI
            trade_summary = await self._format_trades_for_ai(
                trades_with_insiders, company
            )

            # Generate AI analysis
            analysis = await self._generate_company_analysis(
                company.name, ticker, trade_summary, days_back
            )

            return {
                "ticker": ticker,
                "company_name": company.name,
                "days_analyzed": days_back,
                "total_trades": len(trades_with_insiders),
                "timestamp": datetime.utcnow().isoformat(),
                **analysis,
            }

        except Exception as e:
            logger.error(f"Error analyzing company {ticker}: {e}", exc_info=True)
            return {"error": str(e)}

    async def generate_daily_summary(self) -> Optional[Dict[str, Any]]:
        """
        Generate news-feed style summary of recent insider trades grouped by company.

        Returns:
            Dict with company summaries or None if unavailable
        """
        if not self._check_availability():
            return None

        try:
            # Diagnostic: Get total trades count
            total_trades_result = await self.db.execute(select(func.count(Trade.id)))
            total_trades_count = total_trades_result.scalar() or 0
            logger.info(f"[Daily Summary] Total trades in database: {total_trades_count}")

            # Get trades from configured days back
            days_back = getattr(settings, 'ai_insights_days_back', 7)
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            logger.info(f"[Daily Summary] Querying trades from last {days_back} days (cutoff: {cutoff_date.isoformat()})")

            result = await self.db.execute(
                select(Trade, Company, Insider)
                .join(Company, Trade.company_id == Company.id)
                .join(Insider, Trade.insider_id == Insider.id)
                .where(Trade.filing_date >= cutoff_date)
                .order_by(Trade.filing_date.desc())
            )
            trades_data = result.all()

            # Diagnostic: Get trades in last 30 days for comparison
            cutoff_30d = datetime.utcnow() - timedelta(days=30)
            result_30d = await self.db.execute(
                select(func.count(Trade.id)).where(Trade.filing_date >= cutoff_30d)
            )
            trades_30d_count = result_30d.scalar() or 0
            logger.info(f"[Daily Summary] Trades in last 7 days: {len(trades_data)}, last 30 days: {trades_30d_count}")

            if not trades_data:
                logger.warning(
                    f"[Daily Summary] No trades found in last 7 days. "
                    f"Total DB trades: {total_trades_count}, Last 30 days: {trades_30d_count}"
                )
                return {
                    "company_summaries": [],
                    "total_trades": 0,
                    "generated_at": datetime.utcnow().isoformat(),
                    "period": f"last {days_back} days",
                    "diagnostics": {
                        "total_trades_in_db": total_trades_count,
                        "trades_in_last_7_days": 0,
                        "trades_in_last_30_days": trades_30d_count,
                        "days_back_configured": days_back,
                    },
                }

            # Group trades by company
            companies_map = {}
            for trade, company, insider in trades_data:
                ticker = company.ticker
                if ticker not in companies_map:
                    companies_map[ticker] = {
                        "ticker": ticker,
                        "company_name": company.name,
                        "trades": [],
                        "total_value": 0,
                        "buy_count": 0,
                        "sell_count": 0,
                        "insiders": set(),
                    }

                trade_value = await self._get_trade_value(trade)
                companies_map[ticker]["trades"].append(
                    {
                        "insider": insider.name,
                        "role": insider.title or "Insider",
                        "type": trade.transaction_type,
                        "shares": self._get_trade_shares(trade),
                        "value": trade_value,
                        "date": trade.filing_date.isoformat(),
                    }
                )
                companies_map[ticker]["total_value"] += trade_value
                companies_map[ticker]["insiders"].add(insider.name)
                if trade.transaction_type == "BUY":
                    companies_map[ticker]["buy_count"] += 1
                else:
                    companies_map[ticker]["sell_count"] += 1

            # Sort companies by total value (descending)
            sorted_companies = sorted(
                companies_map.values(),
                key=lambda x: x["total_value"],
                reverse=True
            )[:10]  # Top 10 companies
            
            # Generate AI summary for the daily report
            # We aggregate top companies into a single prompt to save API calls
            top_company_data = []
            for company_data in sorted_companies:
                # Convert set to list
                company_data["insiders"] = list(company_data["insiders"])
                top_company_data.append(company_data)

            logger.info(
                f"[Daily Summary] Found {len(companies_map)} companies with trades. "
                f"Top {len(sorted_companies)} companies selected for summary."
            )

            # Generate one comprehensive summary using AI
            ai_daily_overview = await self._generate_daily_overview(top_company_data, len(trades_data))

            # Populate individual company summaries with basic data (no extra AI calls)
            company_summaries = []
            for company_data in top_company_data:
                sentiment = (
                    "buying"
                    if company_data["buy_count"] > company_data["sell_count"]
                    else "selling"
                )
                basic_summary = (
                    f"{company_data['ticker']} insiders showed {sentiment} "
                    f"activity with {len(company_data['trades'])} transactions "
                    f"totaling ${company_data['total_value']:,.0f}."
                )
                
                company_summaries.append(
                    {
                        "ticker": company_data["ticker"],
                        "company_name": company_data["company_name"],
                        "summary": basic_summary, # Use basic summary to save tokens/calls
                        "total_value": company_data["total_value"],
                        "trade_count": len(company_data["trades"]),
                        "buy_count": company_data["buy_count"],
                        "sell_count": company_data["sell_count"],
                        "insider_count": len(company_data["insiders"]),
                        "latest_date": company_data["trades"][0]["date"],
                    }
                )

            return {
                "ai_overview": ai_daily_overview, # New field for the main AI insight
                "company_summaries": company_summaries,
                "total_trades": len(trades_data),
                "generated_at": datetime.utcnow().isoformat(),
                "period": f"last {days_back} days",
                "diagnostics": {
                    "total_trades_in_db": total_trades_count,
                    "trades_in_last_7_days": len(trades_data),
                    "trades_in_last_30_days": trades_30d_count,
                    "days_back_configured": days_back,
                },
            }

        except Exception as e:
            logger.error(f"Error generating daily summary: {e}", exc_info=True)
            return {"error": str(e)}

    async def generate_daily_summary_material_only(self) -> Optional[Dict[str, Any]]:
        """
        Generate daily summary filtering for material trades only.
        
        Material trades: $50K+ value OR 10K+ shares.
        Includes contextual analysis: why it matters, historical context, sector implications.
        """
        if not self._check_availability():
            return None

        try:
            # Get trades from last 24 hours
            cutoff_date = datetime.utcnow() - timedelta(days=1)

            result = await self.db.execute(
                select(Trade, Company, Insider)
                .join(Company, Trade.company_id == Company.id)
                .join(Insider, Trade.insider_id == Insider.id)
                .where(Trade.filing_date >= cutoff_date)
                .order_by(Trade.filing_date.desc())
            )
            all_trades = result.all()

            # Filter for material trades: $50K+ OR 10K+ shares
            material_trades = []
            for trade, company, insider in all_trades:
                trade_value = await self._get_trade_value(trade)
                shares = self._get_trade_shares(trade)
                
                # Material trade criteria
                is_material = (
                    trade_value >= 50000 or  # $50K+ value
                    shares >= 10000  # 10K+ shares
                )
                
                if is_material:
                    material_trades.append((trade, company, insider))

            if not material_trades:
                return {
                    "company_summaries": [],
                    "total_trades": 0,
                    "material_trades": 0,
                    "generated_at": datetime.utcnow().isoformat(),
                    "period": "last 24 hours",
                    "message": "No material trades found in the last 24 hours.",
                }

            # Group material trades by company
            companies_map = {}
            for trade, company, insider in material_trades:
                ticker = company.ticker
                if ticker not in companies_map:
                    companies_map[ticker] = {
                        "ticker": ticker,
                        "company_name": company.name,
                        "trades": [],
                        "total_value": 0,
                        "buy_count": 0,
                        "sell_count": 0,
                        "insiders": set(),
                        "material_trade_count": 0,
                    }

                trade_value = await self._get_trade_value(trade)
                shares = self._get_trade_shares(trade)
                
                companies_map[ticker]["trades"].append({
                    "insider": insider.name,
                    "role": insider.title or "Insider",
                    "type": trade.transaction_type,
                    "shares": shares,
                    "value": trade_value,
                    "date": trade.filing_date.isoformat(),
                })
                companies_map[ticker]["total_value"] += trade_value
                companies_map[ticker]["insiders"].add(insider.name)
                companies_map[ticker]["material_trade_count"] += 1
                
                if trade.transaction_type == "BUY":
                    companies_map[ticker]["buy_count"] += 1
                else:
                    companies_map[ticker]["sell_count"] += 1

            # Sort by total value
            sorted_companies = sorted(
                companies_map.values(),
                key=lambda x: x["total_value"],
                reverse=True
            )[:10]

            # Generate contextual AI analysis with historical context and sector implications
            ai_overview = await self._generate_contextual_daily_analysis(
                sorted_companies, len(material_trades), len(all_trades)
            )

            # Build company summaries
            company_summaries = []
            for company_data in sorted_companies:
                company_data["insiders"] = list(company_data["insiders"])
                company_summaries.append({
                    "ticker": company_data["ticker"],
                    "company_name": company_data["company_name"],
                    "total_value": company_data["total_value"],
                    "trade_count": company_data["material_trade_count"],
                    "buy_count": company_data["buy_count"],
                    "sell_count": company_data["sell_count"],
                    "insider_count": len(company_data["insiders"]),
                    "latest_date": company_data["trades"][0]["date"] if company_data["trades"] else None,
                })

            return {
                "ai_overview": ai_overview,
                "company_summaries": company_summaries,
                "total_trades": len(all_trades),
                "material_trades": len(material_trades),
                "generated_at": datetime.utcnow().isoformat(),
                "period": "last 24 hours",
            }

        except Exception as e:
            logger.error(f"Error generating material-only daily summary: {e}", exc_info=True)
            return {"error": str(e)}

    async def _generate_contextual_daily_analysis(
        self, companies: List[Dict], material_count: int, total_count: int
    ) -> str:
        """
        Generate contextual analysis with:
        - Why it matters
        - Historical context
        - Sector implications
        """
        if not companies:
            return "No material insider trading activity detected in the last 24 hours."

        # Prepare company context
        company_context = []
        for c in companies[:5]:  # Top 5 for context
            insiders_str = ", ".join(list(c["insiders"])[:3])
            company_context.append(
                f"- {c['ticker']} ({c['company_name']}): "
                f"${c['total_value']:,.0f} in material trades "
                f"({c['buy_count']} buys, {c['sell_count']} sells). "
                f"Key insiders: {insiders_str}"
            )

        system_prompt = (
            "You are a senior financial analyst providing contextual analysis of insider trading activity.\n"
            "Provide analysis that includes:\n"
            "1. **Why it matters**: Significance of these trades for investors\n"
            "2. **Historical context**: How this compares to typical activity patterns\n"
            "3. **Sector implications**: What this might indicate about broader sector trends\n\n"
            "Be concise (4-5 sentences) but insightful. Focus on actionable intelligence."
        )

        user_prompt = f"""
        MATERIAL TRADES ANALYSIS (Last 24 Hours):
        
        Total Trades: {total_count}
        Material Trades (≥$50K or ≥10K shares): {material_count}
        
        Top Activity:
        {chr(10).join(company_context)}
        
        Provide contextual analysis explaining why these trades matter, historical context, and sector implications.
        """

        return await self._call_ai_provider(system_prompt, user_prompt, max_tokens=400)

    async def _generate_daily_overview(self, top_companies: List[Dict], total_trade_count: int) -> str:
        """Generate a single AI overview for the entire day's activity."""
        
        # Prepare context for the top 5 companies to keep prompt size manageable
        context_lines = []
        for c in top_companies[:5]:
            insiders_str = ", ".join(c["insiders"][:3])
            context_lines.append(
                f"- {c['ticker']} ({c['company_name']}): ${c['total_value']:,.0f} volume. "
                f"({c['buy_count']} buys, {c['sell_count']} sells). Key insiders: {insiders_str}"
            )
        
        companies_context = "\n".join(context_lines)
        
        system_prompt = (
            "You are a financial news anchor. Write a short, punchy 3-sentence summary "
            "of today's most significant insider trading activity. Focus on the biggest movers."
        )
        
        user_prompt = f"""
        Total Market Trades: {total_trade_count}
        
        Top Activity:
        {companies_context}
        
        Write a 3-sentence market update summarizing this activity.
        """
        
        # Use existing helper to call AI
        return await self._call_ai_provider(system_prompt, user_prompt, max_tokens=200)

    async def _call_ai_provider(self, system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
        """Helper to call configured AI provider with error handling."""
        errors = []
        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = await asyncio.wait_for(
                        self.gemini_client.generate_content_async(
                            full_prompt,
                            generation_config={
                                "temperature": 0.7,
                                "max_output_tokens": max_tokens,
                            },
                        ),
                        timeout=20.0,
                    )
                    return response.text.strip()

                if provider == "openai" and self.openai_client:
                    response = await asyncio.wait_for(
                        self.openai_client.chat.completions.create(
                            model=settings.openai_model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=0.7,
                            max_tokens=max_tokens,
                        ),
                        timeout=20.0,
                    )
                    return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"AI call failed for {provider}: {e}")
                errors.append(f"{provider}: {e}")
                continue
        
        return "AI analysis temporarily unavailable."

    async def ask_question(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Answer natural language questions about insider trades.

        Args:
            question: User's question

        Returns:
            Dict with AI answer or None if unavailable
        """
        if not self._check_availability():
            return None

        try:
            # Get recent trade statistics
            stats = await self._get_trade_statistics()

            # Generate AI response
            answer, response_metadata = await self._generate_chatbot_response(question, stats)

            return {
                "question": question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat(),
                "response_metadata": response_metadata,
            }

        except Exception as e:
            logger.error(f"Error answering question: {e}", exc_info=True)
            return {"error": str(e)}

    async def generate_trading_signals(self) -> Optional[Dict[str, Any]]:
        """
        Generate AI-powered trading signals based on insider activity.

        Returns:
            Dict with trading signals or None if unavailable
        """
        if not self._check_availability():
            return None

        try:
            # Get companies with significant recent activity
            days_back = getattr(settings, 'ai_insights_days_back', 7)
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            logger.info(f"[Trading Signals] Querying trades from last {days_back} days (cutoff: {cutoff_date.isoformat()})")

            # Group trades by company
            result = await self.db.execute(
                select(
                    Company.id,
                    Company.ticker,
                    Company.name,
                    func.count(Trade.id).label("trade_count"),
                    func.sum(
                        case((Trade.transaction_type == "BUY", Trade.shares), else_=0)
                    ).label("buy_volume"),
                    func.sum(
                        case((Trade.transaction_type == "SELL", Trade.shares), else_=0)
                    ).label("sell_volume"),
                    func.sum(
                        case((Trade.transaction_type == "BUY", Trade.total_value), else_=0)
                    ).label("buy_value"),
                    func.sum(
                        case((Trade.transaction_type == "SELL", Trade.total_value), else_=0)
                    ).label("sell_value"),
                )
                .join(Trade, Company.id == Trade.company_id)
                .where(Trade.filing_date >= cutoff_date)
                .group_by(Company.id, Company.ticker, Company.name)
                .having(func.count(Trade.id) >= 3)
                .order_by(desc("trade_count"))
                .limit(10)
            )
            companies = result.all()

            if not companies:
                return {
                    "signals": [],
                    "message": "No significant insider trading activity detected in the last 7 days.",
                    "generated_at": datetime.utcnow().isoformat(),
                    "period": "7 days",
                }

            logger.info(f"[Trading Signals] Generating signals for {len(companies)} companies")

            # Generate signals
            signals = await self._generate_signals(companies)

            return {
                "signals": signals,
                "generated_at": datetime.utcnow().isoformat(),
                "period": f"{days_back} days",
                "diagnostics": {
                    "total_trades_in_db": total_trades_count,
                    "trades_in_last_7_days": len(all_companies),
                    "trades_in_last_30_days": trades_30d_count,
                    "companies_with_trades": len(all_companies),
                    "companies_meeting_criteria": len(companies),
                    "days_back_configured": days_back,
                },
            }

        except Exception as e:
            logger.error(f"Error generating trading signals: {e}", exc_info=True)
            return {"error": str(e)}

    # Private helper methods

    @staticmethod
    def _get_trade_shares(trade: Trade) -> float:
        """Return trade shares as float."""
        shares = getattr(trade, "shares", None)
        return float(shares) if shares is not None else 0.0

    async def _get_trade_value(self, trade: Trade) -> float:
        """Return trade value using stored total, estimation, or calculated fallback."""
        total_value = getattr(trade, "total_value", None)
        if total_value is not None and total_value > 0:
            return float(total_value)

        # Try estimation service for missing values
        try:
            from app.services.trade_value_estimation_service import (
                TradeValueEstimationService,
            )

            value_service = TradeValueEstimationService(self.db)
            estimates = await value_service.estimate_missing_trade_value(trade)
            estimated_value = estimates.get("total_value", 0)
            if estimated_value > 0:
                return estimated_value
        except Exception as e:
            logger.debug(f"Could not estimate trade value: {e}")

        # Fallback: calculate from shares and price
        shares = getattr(trade, "shares", None)
        price = getattr(trade, "price_per_share", None)
        if shares is not None and price is not None:
            return float(shares * price)

        return 0.0

    async def _format_trades_for_ai(
        self, trades_with_insiders: List[tuple], company: Company
    ) -> str:
        """Format trades into a summary for AI analysis."""
        buy_trades = []
        sell_trades = []
        total_buy_value = 0
        total_sell_value = 0

        for trade, insider in trades_with_insiders:
            shares = self._get_trade_shares(trade)
            value = await self._get_trade_value(trade)
            trade_info = {
                "insider": insider.name,
                "role": insider.title or "Insider",
                "shares": shares,
                "value": value,
                "date": trade.filing_date.strftime("%Y-%m-%d"),
            }

            if trade.transaction_type == "BUY":
                buy_trades.append(trade_info)
                total_buy_value += trade_info["value"]
            else:
                sell_trades.append(trade_info)
                total_sell_value += trade_info["value"]

        summary = f"Company: {company.name} ({company.ticker})\n\n"
        summary += f"Total Buy Trades: {len(buy_trades)} (${total_buy_value:,.0f})\n"
        summary += (
            f"Total Sell Trades: {len(sell_trades)} (${total_sell_value:,.0f})\n\n"
        )

        if buy_trades:
            summary += "Recent BUY Trades:\n"
            for t in buy_trades[:5]:
                summary += (
                    f"- {t['insider']} ({t['role']}): {t['shares']:,.0f} shares, "
                    f"${t['value']:,.0f} on {t['date']}\n"
                )

        if sell_trades:
            summary += "\nRecent SELL Trades:\n"
            for t in sell_trades[:5]:
                summary += (
                    f"- {t['insider']} ({t['role']}): {t['shares']:,.0f} shares, "
                    f"${t['value']:,.0f} on {t['date']}\n"
                )

        return summary

    async def _generate_company_analysis(
        self, company_name: str, ticker: str, trade_summary: str, days_back: int
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI-powered analysis for a company.

        Integrates multiple data sources when enabled:
        - Insider trading patterns (always)
        - Technical analysis (if enabled)
        - Fundamental analysis (if enabled)
        - News sentiment (if enabled)
        - Analyst ratings (if enabled)
        """
        # Gather all available data sources
        technical_data = await self._get_technical_context(ticker)
        fundamental_data = await self._get_fundamental_context(ticker)
        news_data = await self._get_news_context(ticker)
        analyst_data = await self._get_analyst_context(ticker)

        # Check if price predictions are enabled
        enable_predictions = settings.enable_price_predictions

        # Build enhanced system prompt
        if enable_predictions and any([technical_data, fundamental_data, analyst_data]):
            system_prompt = (
                "You are LUNA, TradeSignal's advanced AI stock analyst with expertise in:\n"
                "- Insider trading patterns\n"
                "- Technical analysis\n"
                "- Fundamental analysis\n"
                "- Market sentiment\n"
                "- Quantitative modeling\n\n"
                "Provide comprehensive analysis synthesizing ALL available data sources.\n\n"
                "Respond ONLY in this exact JSON format:\n"
                "{\n"
                '  "analysis": "3-4 sentence analytical summary synthesizing ALL data sources",\n'
                '  "sentiment": "BULLISH|BEARISH|NEUTRAL",\n'
                '  "confidence": "HIGH|MEDIUM|LOW",\n'
                '  "price_predictions": [\n'
                '    {"timeframe": "1week", "target_price": 0.00, "upside_pct": 0.0, "probability": 0.0},\n'
                '    {"timeframe": "1month", "target_price": 0.00, "upside_pct": 0.0, "probability": 0.0},\n'
                '    {"timeframe": "3months", "target_price": 0.00, "upside_pct": 0.0, "probability": 0.0},\n'
                '    {"timeframe": "6months", "target_price": 0.00, "upside_pct": 0.0, "probability": 0.0}\n'
                '  ],\n'
                '  "recommendation": "BUY|HOLD|SELL",\n'
                '  "risk_level": "HIGH|MEDIUM|LOW",\n'
                '  "insights": ["insight 1 combining multiple data sources", "insight 2", "insight 3", "insight 4"],\n'
                '  "catalysts": ["catalyst 1", "catalyst 2"],\n'
                '  "risks": ["risk 1", "risk 2"],\n'
                f'  "disclaimer": "{settings.price_prediction_disclaimer}"\n'
                "}\n\n"
                "Be analytical and quantitative. Provide specific price targets with reasoning."
            )
        else:
            # Original prompt for insider-only analysis
            system_prompt = (
                "You are LUNA, TradeSignal's advanced AI financial analyst specializing in forensic "
                "insider trading analysis and 'follow the money' logic.\n\n"
                "Analyze the provided SEC Form 4 data with the skepticism of a short-seller "
                "and the conviction of a value investor. Focus on conviction levels.\n\n"
                "Provide a comprehensive analysis with:\n"
                "1. **Analysis**: 3-5 sentence rigorous summary. Connect dots between "
                "different insiders, roles, and transaction sizes. What is the hidden signal?\n\n"
                "2. **Sentiment**: BULLISH, BEARISH, or NEUTRAL based on conviction levels.\n\n"
                "3. **Key Insights** (4-6 bullet points):\n"
                "   - Pattern Recognition: Cluster buying/selling, systematic timing.\n"
                "   - Role Significance: Why does this trade matter specifically for a CEO vs a Director?\n"
                "   - Magnitude Assessment: Is this a material bet or pocket change?\n"
                "   - Conviction Signal: Distinguish between routine diversification and strategic positioning.\n"
                "   - Actionable Intelligence: The 'so what' for a retail investor.\n\n"
                "Be sharp, analytical, and quantitative. Use terms like 'high-conviction', 'material accumulation', "
                "or 'liquidity-driven' where appropriate.\n\n"
                "Respond ONLY in this exact JSON format:\n"
                "{\n"
                '  "analysis": "your detailed forensic summary",\n'
                '  "sentiment": "BULLISH|BEARISH|NEUTRAL",\n'
                '  "insights": ["insight 1", "insight 2", "insight 3", "insight 4"]\n'
                "}"
            )

        # Build comprehensive user prompt with all available data
        prompt_parts = [
            f"Analyze {company_name} ({ticker}) over the past {days_back} days.\n"
        ]

        # Always include insider trading data
        prompt_parts.append(f"**INSIDER TRADING DATA:**\n{trade_summary}\n")

        # Add technical data if available
        if technical_data:
            prompt_parts.append(
                f"**TECHNICAL ANALYSIS:**\n{json.dumps(technical_data, indent=2)}\n"
            )

        # Add fundamental data if available
        if fundamental_data:
            prompt_parts.append(
                f"**FUNDAMENTAL ANALYSIS:**\n{json.dumps(fundamental_data, indent=2)}\n"
            )

        # Add news data if available
        if news_data:
            prompt_parts.append(
                f"**NEWS & SENTIMENT:**\n{json.dumps(news_data, indent=2)}\n"
            )

        # Add analyst data if available
        if analyst_data:
            prompt_parts.append(
                f"**ANALYST RATINGS:**\n{json.dumps(analyst_data, indent=2)}\n"
            )

        if enable_predictions and any([technical_data, fundamental_data, analyst_data]):
            prompt_parts.append(
                "\nProvide comprehensive analysis with specific price predictions for each timeframe. "
                "Base predictions on ALL available data sources."
            )
        else:
            prompt_parts.append(
                "\nRemember: Be analytical and insightful, not just descriptive. "
                "What do these trades really tell us?"
            )

        user_prompt = "\n".join(prompt_parts)

        errors: List[str] = []

        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    # Add 20 second timeout for company analysis
                    response = await asyncio.wait_for(
                        self.gemini_client.generate_content_async(
                            full_prompt,
                            generation_config={
                                "temperature": settings.ai_temperature,
                                "max_output_tokens": settings.ai_max_tokens,
                            },
                        ),
                        timeout=20.0,
                    )
                    parsed = self._parse_json_response(response.text)
                    if parsed is None:
                        raise ValueError("Gemini response was not valid JSON")
                    self.provider = provider
                    return parsed

                if provider == "openai" and self.openai_client:
                    # Add 20 second timeout for company analysis
                    response = await asyncio.wait_for(
                        self.openai_client.chat.completions.create(
                            model=settings.openai_model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=settings.ai_temperature,
                            max_tokens=settings.ai_max_tokens,
                            response_format={"type": "json_object"},
                        ),
                        timeout=20.0,
                    )
                    parsed = self._parse_json_response(
                        response.choices[0].message.content
                    )
                    if parsed is None:
                        raise ValueError("OpenAI response was not valid JSON")
                    self.provider = provider
                    return parsed
            except asyncio.TimeoutError:
                logger.warning(f"AI timeout for {provider} generating company analysis")
                errors.append(f"{provider}: timeout")
                continue
            except Exception as e:
                logger.error(f"AI API error ({provider}): {e}", exc_info=True)
                errors.append(f"{provider}: {e}")
                continue

        return {
            "analysis": "Unable to generate AI analysis at this time.",
            "sentiment": "NEUTRAL",
            "insights": [],
            "error": "; ".join(errors) if errors else "No AI provider available",
        }

    async def _generate_daily_summary(
        self, top_trades: List[Dict], total_count: int
    ) -> str:
        """Generate daily summary text with rich AI-powered insights."""
        system_prompt = (
            "You are an expert financial analyst specializing in insider trading "
            "analysis.\n"
            "Write an insightful daily summary that goes beyond simple facts. "
            "Consider:\n"
            "- Transaction patterns (clustering, timing, unusual activity)\n"
            "- Insider roles and their significance (C-suite vs directors)\n"
            "- Trade sizes relative to typical activity\n"
            "- Sector trends or concentrations\n"
            "- Potential market implications\n\n"
            "Be concise (4-5 sentences) but analytical. Use professional yet "
            "engaging language that provides real value to investors."
        )

        # Enrich trade data with context
        trades_by_company = {}
        total_buy_value = 0
        total_sell_value = 0
        c_suite_trades = []

        for t in top_trades:
            ticker = t["ticker"]
            if ticker not in trades_by_company:
                trades_by_company[ticker] = {"buy": 0, "sell": 0, "insiders": []}

            if t["type"] == "BUY":
                total_buy_value += t["value"]
                trades_by_company[ticker]["buy"] += t["value"]
            else:
                total_sell_value += t["value"]
                trades_by_company[ticker]["sell"] += t["value"]

            role = t["role"].upper()
            if any(
                title in role for title in ["CEO", "CFO", "COO", "PRESIDENT", "CHIEF"]
            ):
                c_suite_trades.append(f"{t['ticker']} {t['insider']} ({t['role']})")

            trades_by_company[ticker]["insiders"].append(t["insider"])

        # Calculate insights
        buy_sell_ratio = (
            (total_buy_value / total_sell_value * 100) if total_sell_value > 0 else 100
        )
        companies_with_activity = len(trades_by_company)

        # Format detailed trade information
        trades_text = "\n".join(
            [
                f"{t['ticker']} - {t['company']}: {t['insider']} ({t['role']}) "
                f"{t['type']} {t['shares']:,.0f} shares @ ${t['value']:,.0f} "
                f"on {t['date']}"
                for t in top_trades[:10]
            ]
        )

        user_prompt = f"""Analyze today's insider trading activity and write an insightful summary:

OVERALL METRICS:
- Total trades: {total_count}
- Companies with activity: {companies_with_activity}
- Total buy value: ${total_buy_value:,.0f}
- Total sell value: ${total_sell_value:,.0f}
- Buy/Sell ratio: {buy_sell_ratio:.1f}%
- C-suite executives involved: {len(c_suite_trades)}

TOP TRADES (chronological):
{trades_text}

NOTABLE C-SUITE ACTIVITY:
{chr(10).join(c_suite_trades[:5]) if c_suite_trades else "None"}

Write a 4-5 sentence analysis that identifies patterns, highlights significant
trades, and provides actionable insights for investors."""

        errors: List[str] = []

        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    # Add 20 second timeout for daily summary
                    response = await asyncio.wait_for(
                        self.gemini_client.generate_content_async(
                            full_prompt,
                            generation_config={
                                "temperature": settings.ai_temperature,
                                "max_output_tokens": 300,
                            },
                        ),
                        timeout=20.0,
                    )
                    self.provider = provider
                    return response.text.strip()

                if provider == "openai" and self.openai_client:
                    # Add 20 second timeout for daily summary
                    response = await asyncio.wait_for(
                        self.openai_client.chat.completions.create(
                            model=settings.openai_model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=settings.ai_temperature,
                            max_tokens=300,
                        ),
                        timeout=20.0,
                    )
                    self.provider = provider
                    return response.choices[0].message.content.strip()
            except asyncio.TimeoutError:
                logger.warning(f"AI timeout for {provider} generating daily summary")
                errors.append(f"{provider}: timeout")
                continue
            except Exception as e:
                logger.error(f"AI API error ({provider}): {e}", exc_info=True)
                errors.append(f"{provider}: {e}")
                continue

        highlighted = [
            trade["ticker"] for trade in top_trades[:2] if trade.get("ticker")
        ]
        if highlighted:
            joined = (
                " and ".join(highlighted) if len(highlighted) > 1 else highlighted[0]
            )
            return (
                f"Today saw {total_count} insider trades, including notable activity "
                f"in {joined}. (AI unavailable: "
                f"{ '; '.join(errors) if errors else 'no provider' })"
            )
        return (
            f"Today saw {total_count} insider trades. (AI unavailable: "
            f"{ '; '.join(errors) if errors else 'no provider' })"
        )

    @staticmethod
    def _parse_json_response(raw_text: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse JSON returned by AI providers, handling fenced blocks."""
        if not raw_text:
            return None

        text = raw_text.strip()
        lower_text = text.lower()
        for fence in ("```json", "```"):
            if lower_text.startswith(fence):
                text = text[len(fence) :].strip()
                break
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    async def _get_trade_statistics(self) -> Dict[str, Any]:
        """Get recent trade statistics for chatbot context."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Get basic stats
        result = await self.db.execute(
            select(
                func.count(Trade.id).label("total_trades"),
                func.sum(case((Trade.transaction_type == "BUY", 1), else_=0)).label(
                    "buy_trades"
                ),
                func.sum(case((Trade.transaction_type == "SELL", 1), else_=0)).label(
                    "sell_trades"
                ),
            ).where(Trade.filing_date >= cutoff_date)
        )
        stats = result.first()

        return {
            "total_trades": stats.total_trades or 0,
            "buy_trades": stats.buy_trades or 0,
            "sell_trades": stats.sell_trades or 0,
            "period_days": 30,
        }

    async def _generate_chatbot_response(
        self, question: str, stats: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Generate intelligent, context-aware chatbot responses with real data."""
        buy_sell_ratio = (stats["buy_trades"] / max(stats["sell_trades"], 1)) * 100
        market_sentiment = (
            "bullish"
            if buy_sell_ratio > 60
            else "bearish"
            if buy_sell_ratio < 40
            else "neutral"
        )

        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Get ALL companies with activity (not just top 10)
        all_companies_result = await self.db.execute(
            select(Company.ticker, Company.name)
            .join(Trade, Company.id == Trade.company_id)
            .where(Trade.filing_date >= cutoff_date)
            .group_by(Company.ticker, Company.name)
        )
        all_companies = all_companies_result.all()

        # Get top 20 buying activity with insider details (increased from 10)
        top_buyers_result = await self.db.execute(
            select(
                Company.ticker,
                Company.name,
                Insider.name.label("insider_name"),
                Insider.relationship,
                func.count(Trade.id).label("buy_count"),
                func.sum(
                    case((Trade.transaction_type == "BUY", Trade.total_value), else_=0)
                ).label("total_buy_value"),
            )
            .join(Trade, Company.id == Trade.company_id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
            .where(Trade.transaction_type == "BUY")
            .group_by(Company.ticker, Company.name, Insider.name, Insider.relationship)
            .order_by(
                func.sum(
                    case((Trade.transaction_type == "BUY", Trade.total_value), else_=0)
                ).desc()
            )
            .limit(20)
        )
        top_buyers = top_buyers_result.all()

        # Get top 20 selling activity with insider details (increased from 10)
        top_sellers_result = await self.db.execute(
            select(
                Company.ticker,
                Company.name,
                Insider.name.label("insider_name"),
                Insider.relationship,
                func.count(Trade.id).label("sell_count"),
                func.sum(
                    case((Trade.transaction_type == "SELL", Trade.total_value), else_=0)
                ).label("total_sell_value"),
            )
            .join(Trade, Company.id == Trade.company_id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
            .where(Trade.transaction_type == "SELL")
            .group_by(Company.ticker, Company.name, Insider.name, Insider.relationship)
            .order_by(
                func.sum(
                    case((Trade.transaction_type == "SELL", Trade.total_value), else_=0)
                ).desc()
            )
            .limit(20)
        )
        top_sellers = top_sellers_result.all()

        # Get top insiders by share volume (ALL ROLES - CEO, CFO, Director, Officer, etc.)
        top_insiders_volume_result = await self.db.execute(
            select(
                Company.ticker,
                Insider.name.label("insider_name"),
                Insider.relationship,
                func.count(Trade.id).label("buy_count"),
                func.sum(Trade.shares).label("total_shares"),
                func.sum(Trade.total_value).label("total_value"),
            )
            .join(Trade, Company.id == Trade.company_id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
            .where(Trade.transaction_type == "BUY")
            .group_by(Company.ticker, Insider.name, Insider.relationship)
            .order_by(func.sum(Trade.shares).desc())
            .limit(30)  # Top 30 insiders by share volume (all roles)
        )
        top_insiders_volume = top_insiders_volume_result.all()

        # Get most active insiders by trade count (ALL ROLES)
        most_active_insiders_result = await self.db.execute(
            select(
                Company.ticker,
                Insider.name.label("insider_name"),
                Insider.relationship,
                func.count(Trade.id).label("trade_count"),
                func.sum(case((Trade.transaction_type == "BUY", 1), else_=0)).label(
                    "buy_count"
                ),
                func.sum(case((Trade.transaction_type == "SELL", 1), else_=0)).label(
                    "sell_count"
                ),
            )
            .join(Trade, Company.id == Trade.company_id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
            .group_by(Company.ticker, Insider.name, Insider.relationship)
            .order_by(func.count(Trade.id).desc())
            .limit(20)  # Top 20 most active insiders
        )
        most_active_insiders = most_active_insiders_result.all()

        # Get insider role distribution
        insider_roles_result = await self.db.execute(
            select(
                Insider.relationship,
                func.count(func.distinct(Insider.id)).label("insider_count"),
                func.count(Trade.id).label("trade_count"),
            )
            .join(Trade, Insider.id == Trade.insider_id)
            .where(Trade.filing_date >= cutoff_date)
            .group_by(Insider.relationship)
            .order_by(func.count(Trade.id).desc())
            .limit(15)  # Top 15 insider role types
        )
        insider_roles = insider_roles_result.all()

        # Format data for AI context
        def format_value(value):
            if value is None or value == 0:
                return "Not Disclosed"
            return f"${value:,.0f}"

        # List ALL companies with activity
        all_companies_list = ", ".join(
            [row.ticker for row in all_companies[:50]]
        )  # Show first 50
        if len(all_companies) > 50:
            all_companies_list += f" (and {len(all_companies) - 50} more)"

        if top_buyers:
            top_buyers_list = "\n".join(
                [
                    f"- {row.ticker}: {row.insider_name} "
                    f"({row.relationship or 'Insider'}) - {row.buy_count} buys, "
                    f"{format_value(row.total_buy_value)}"
                    for row in top_buyers[:10]
                ]
            )
        else:
            top_buyers_list = (
                "No significant insider buying activity in the last 30 days."
            )

        if top_sellers:
            top_sellers_list = "\n".join(
                [
                    f"- {row.ticker}: {row.insider_name} "
                    f"({row.relationship or 'Insider'}) - {row.sell_count} sells, "
                    f"{format_value(row.total_sell_value)}"
                    for row in top_sellers[:10]
                ]
            )
        else:
            top_sellers_list = (
                "No significant insider selling activity in the last 30 days."
            )

        # Format top insiders by share volume
        if top_insiders_volume:
            top_insiders_list = "\n".join(
                [
                    f"- {row.ticker}: {row.insider_name} "
                    f"({row.relationship or 'Insider'}) - {row.total_shares:,.0f} "
                    f"shares, {format_value(row.total_value)}"
                    for row in top_insiders_volume[:15]  # Show top 15
                ]
            )
        else:
            top_insiders_list = "No insider buying activity in the last 30 days."

        # Format most active insiders
        if most_active_insiders:
            most_active_list = "\n".join(
                [
                    f"- {row.ticker}: {row.insider_name} "
                    f"({row.relationship or 'Insider'}) - {row.trade_count} trades "
                    f"({row.buy_count} buys, {row.sell_count} sells)"
                    for row in most_active_insiders[:10]  # Show top 10
                ]
            )
        else:
            most_active_list = "No active insiders in the last 30 days."

        # Format insider role distribution
        if insider_roles:
            insider_roles_list = "\n".join(
                [
                    f"- {row.relationship}: {row.insider_count} insiders, "
                    f"{row.trade_count} trades"
                    for row in insider_roles[:10]  # Show top 10 roles
                ]
            )
        else:
            insider_roles_list = "No insider role data available."

        # Get recent trade examples for context (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_trades_result = await self.db.execute(
            select(Trade, Company, Insider)
            .join(Company, Trade.company_id == Company.id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= recent_cutoff)
            .order_by(Trade.filing_date.desc())
            .limit(10)
        )
        recent_trades_data = recent_trades_result.all()

        # Format recent trades for context
        recent_trades_list = ""
        if recent_trades_data:
            recent_trades_list = "\nRECENT TRADE EXAMPLES (Last 7 Days):\n"
            for trade, company, insider in recent_trades_data[:10]:
                trade_value = await self._get_trade_value(trade)
                value_str = (
                    f"${trade_value:,.0f}" if trade_value > 0 else "Not Disclosed"
                )
                recent_trades_list += (
                    f"- {company.ticker}: {insider.name} "
                    f"({insider.relationship or 'Insider'}) {trade.transaction_type} "
                    f"{trade.shares:,.0f} shares @ {value_str} on "
                    f"{trade.filing_date.strftime('%Y-%m-%d')}\n"
                )
        else:
            recent_trades_list = (
                "\nRECENT TRADE EXAMPLES: No trades in the last 7 days.\n"
            )

        system_prompt = (
            f"You are LUNA, TradeSignal's advanced AI analyst with COMPLETE DATABASE ACCESS to ALL "
            f"{len(all_companies)} companies with insider trading activity.\n\n"
            f"""DATABASE COVERAGE (Last 30 Days):
- Total Companies Tracked: {len(all_companies)}
- Total Trades: {stats['total_trades']:,}
- Buy Transactions: {stats['buy_trades']:,} ({(stats['buy_trades']/max(stats['total_trades'],1)*100):.1f}%)
- Sell Transactions: {stats['sell_trades']:,} ({(stats['sell_trades']/max(stats['total_trades'],1)*100):.1f}%)
- Market Sentiment: {market_sentiment.upper()}

ALL COMPANIES WITH ACTIVITY:
{all_companies_list}

TOP 10 INSIDER BUYING ACTIVITY (by value):
{top_buyers_list}

TOP 10 INSIDER SELLING ACTIVITY (by value):
{top_sellers_list}

TOP INSIDERS BY SHARE VOLUME (ALL ROLES - CEO, CFO, Directors, Officers, etc.):
{top_insiders_list}

MOST ACTIVE INSIDERS BY TRADE COUNT (ALL ROLES):
{most_active_list}

INSIDER ROLE DISTRIBUTION:
{insider_roles_list}
{recent_trades_list}

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:
1. ANSWER THE USER'S QUESTION DIRECTLY. Do not start with "I am LUNA..." or repeat these instructions.
2. You have access to data from ALL {len(all_companies)} companies listed above
3. You have data on ALL INSIDER ROLES: CEOs, CFOs, Directors, Officers,
   10% Owners, Presidents, VPs, etc.
4. The "top" lists are just examples - you can query any company or insider
   from the full database
5. When asked about "biggest trades", cite the SPECIFIC INSIDERS and their
   ROLES from the lists above
6. Format: "[Insider Name] ([Title/Role]) at [Ticker] bought/sold [amount]"
7. If a value shows "Not Disclosed", explain the SEC filing didn't include
   the value
8. NEVER say "I'm not sure" or "I don't have access" - you have complete
   database access
9. Be PRECISE and CONFIDENT - this is real SEC Form 4 data from the last
   30 days
10. When discussing insiders, mention their specific roles (CEO, CFO,
   Director, etc.) to provide context
11. Use the insider role distribution to provide insights about which types
    of insiders are most active
12. Reference specific recent trades when relevant to show you're using
    real-time data
13. Provide quantitative details (trade counts, values, dates) when available
14. Compare and contrast different companies/insiders when asked about trends
15. Be analytical, not just descriptive - explain what the data means

Answer using this real-time data from the complete insider trading database.
Be specific, cite numbers, and reference actual insiders and companies."""
        )

        errors: List[str] = []

        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\nUser question: {question}"
                    # Extended timeout (90s) for chat responses to allow longer response generation
                    response = await asyncio.wait_for(
                        self.gemini_client.generate_content_async(
                            full_prompt,
                            generation_config={
                                "temperature": 0.2,  # Very low temperature for maximum precision
                                "max_output_tokens": 8192,  # Maximum for Gemini 2.0 - allows longer responses
                            },
                        ),
                        timeout=90.0,
                    )
                    self.provider = provider
                    
                    # Extract response text - handle both response.text and candidates/parts for complete extraction
                    response_text = ""
                    extraction_method = "unknown"
                    
                    # Try primary method: response.text (works for most cases)
                    if hasattr(response, 'text') and response.text:
                        response_text = response.text.strip()
                        extraction_method = "response.text"
                    
                    # Fallback: extract from candidates/parts (for long responses that might be split or incomplete)
                    # This is especially important for very long responses that might not be fully captured in response.text
                    if hasattr(response, 'candidates') and response.candidates:
                        try:
                            candidate = response.candidates[0]
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                # Concatenate all parts to ensure complete response
                                parts_text = []
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        parts_text.append(part.text)
                                if parts_text:
                                    candidates_text = " ".join(parts_text).strip()
                                    # Use candidates/parts if it's longer (more complete) or if response.text was empty
                                    if len(candidates_text) > len(response_text):
                                        response_text = candidates_text
                                        extraction_method = "candidates/parts"
                                        logger.debug(
                                            f"[LUNA Response] Extracted response from {len(parts_text)} parts "
                                            f"(total length: {len(response_text)} chars) - "
                                            f"longer than response.text ({len(response.text.strip()) if hasattr(response, 'text') and response.text else 0} chars)"
                                        )
                                    elif not response_text and len(candidates_text) > 0:
                                        # Use candidates if response.text was empty
                                        response_text = candidates_text
                                        extraction_method = "candidates/parts"
                                        logger.debug(
                                            f"[LUNA Response] Extracted response from {len(parts_text)} parts "
                                            f"(total length: {len(response_text)} chars) - "
                                            f"response.text was empty"
                                        )
                        except (AttributeError, IndexError) as e:
                            logger.warning(
                                f"[LUNA Response] Error extracting from candidates/parts: {e}. "
                                f"Using response.text if available."
                            )
                    
                    response_length = len(response_text)
                    
                    # Log extraction method for debugging
                    if response_length > 0:
                        logger.debug(
                            f"[LUNA Response] Extracted using {extraction_method}, "
                            f"length: {response_length} chars"
                        )
                    
                    # Log response details with extraction info
                    if response_length == 0:
                        logger.warning(
                            f"[LUNA Response] Provider: {provider}, Empty response received. "
                            f"Question length: {len(question)} chars"
                        )
                    else:
                        logger.info(
                            f"[LUNA Response] Provider: {provider}, Length: {response_length} chars, "
                            f"Max tokens: 8192, Question length: {len(question)} chars"
                        )
                    
                    # Build metadata
                    metadata = {
                        "provider": provider,
                        "response_length": response_length,
                        "max_tokens": 8192,  # Maximum for Gemini 2.0 - allows longer responses
                        "truncated": False,
                        "safety_blocked": False,
                        "finish_reason": None,
                    }
                    
                    # Check for safety blocks (keep safety detection, remove length-based truncation checks)
                    safety_blocked = False
                    block_reason = None
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        if hasattr(feedback, 'block_reason') and feedback.block_reason:
                            safety_blocked = True
                            block_reason = str(feedback.block_reason)
                            logger.warning(
                                f"[LUNA Response] Safety filter blocked: {feedback.block_reason}"
                            )
                        if hasattr(feedback, 'safety_ratings'):
                            for rating in feedback.safety_ratings:
                                if hasattr(rating, 'blocked') and rating.blocked:
                                    safety_blocked = True
                                    block_reason = f"{rating.category} blocked"
                                    logger.warning(
                                        f"[LUNA Response] Safety rating blocked: {rating.category} - {rating.probability}"
                                    )
                    
                    metadata["safety_blocked"] = safety_blocked
                    if block_reason:
                        metadata["block_reason"] = block_reason
                    
                    # Verify response completeness
                    # Check if response appears complete (ends with punctuation or is very short)
                    appears_complete = (
                        response_length == 0 or
                        response_text.endswith('.') or
                        response_text.endswith('!') or
                        response_text.endswith('?') or
                        response_text.endswith('\n') or
                        response_length < 100  # Very short responses are likely complete
                    )
                    
                    # Log completion status with verification
                    if safety_blocked:
                        logger.warning(
                            f"[LUNA Response] Response blocked by safety filter. "
                            f"Length: {response_length} chars, Reason: {block_reason}"
                        )
                    elif response_length == 0:
                        logger.warning(
                            f"[LUNA Response] Empty response received from Gemini. "
                            f"Check if prompt was blocked or model returned no content."
                        )
                    elif not appears_complete:
                        logger.warning(
                            f"[LUNA Response] Response may be incomplete - doesn't end with punctuation. "
                            f"Length: {response_length} chars, Last 50 chars: '{response_text[-50:]}'"
                        )
                    else:
                        logger.info(
                            f"[LUNA Response] Response completed successfully. "
                            f"Length: {response_length} chars, Appears complete: {appears_complete}"
                        )
                    
                    # Log first and last 100 chars for debugging (only if very long)
                    if response_length > 1000:
                        logger.debug(
                            f"[LUNA Response] First 100 chars: {response_text[:100]}... "
                            f"Last 100 chars: ...{response_text[-100:]}"
                        )
                    
                    return response_text, metadata

                if provider == "openai" and self.openai_client:
                    # Extended timeout (90s) for chat responses to allow longer response generation
                    response = await asyncio.wait_for(
                        self.openai_client.chat.completions.create(
                            model=settings.openai_model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": question},
                            ],
                            temperature=0.2,  # Very low temperature for maximum precision
                            max_tokens=16384,  # Maximum for GPT-4o/GPT-4o-mini - allows longer responses without truncation
                        ),
                        timeout=90.0,
                    )
                    self.provider = provider
                    
                    # Extract response content
                    response_text = response.choices[0].message.content.strip() if response.choices else ""
                    response_length = len(response_text)
                    
                    # Get token usage info
                    usage = getattr(response, 'usage', None)
                    tokens_used = None
                    if usage:
                        tokens_used = getattr(usage, 'completion_tokens', None)
                    
                    # Check for truncation (OpenAI sets finish_reason to 'length' if truncated)
                    finish_reason = response.choices[0].finish_reason if response.choices else None
                    
                    # Log response details with completion status
                    completion_status = "truncated" if finish_reason == 'length' else "completed successfully"
                    logger.info(
                        f"[LUNA Response] Provider: {provider}, Length: {response_length} chars, "
                        f"Tokens used: {tokens_used}, Max tokens: 16384, Question length: {len(question)} chars, "
                        f"Status: {completion_status}, Finish reason: {finish_reason or 'stop'}"
                    )
                    
                    # Build metadata
                    metadata = {
                        "provider": provider,
                        "response_length": response_length,
                        "tokens_used": tokens_used,
                        "max_tokens": 16384,  # Maximum for GPT-4o/GPT-4o-mini - allows longer responses
                        "truncated": False,
                        "safety_blocked": False,
                        "finish_reason": finish_reason,
                    }
                    
                    # Check for truncation and safety blocks (only use actual provider signals)
                    is_truncated = finish_reason == 'length'
                    is_blocked = finish_reason == 'content_filter'
                    
                    metadata["truncated"] = is_truncated
                    metadata["safety_blocked"] = is_blocked
                    
                    if is_truncated:
                        logger.warning(
                            f"[LUNA Response] Response truncated by token limit (actual provider truncation). "
                            f"Length: {response_length} chars, Tokens: {tokens_used}/16384. "
                            f"Consider asking a more specific question or breaking it into parts."
                        )
                    elif is_blocked:
                        logger.warning(
                            f"[LUNA Response] Response blocked by content filter. "
                            f"Length: {response_length} chars"
                        )
                        metadata["block_reason"] = "Content filter blocked response"
                    elif finish_reason:
                        logger.debug(f"[LUNA Response] Finish reason: {finish_reason}")
                    else:
                        # Response completed successfully
                        logger.info(
                            f"[LUNA Response] Response completed successfully. "
                            f"Length: {response_length} chars, Tokens: {tokens_used}, "
                            f"No truncation detected."
                        )
                    
                    # Log first and last 100 chars for debugging (only if very long)
                    if response_length > 1000:
                        logger.debug(
                            f"[LUNA Response] First 100 chars: {response_text[:100]}... "
                            f"Last 100 chars: ...{response_text[-100:]}"
                        )
                    
                    return response_text, metadata
            except asyncio.TimeoutError:
                logger.warning(f"AI timeout for {provider} answering question")
                errors.append(f"{provider}: timeout")
                continue
            except Exception as e:
                logger.error(f"AI API error ({provider}): {e}", exc_info=True)
                errors.append(f"{provider}: {e}")
                continue

        # All providers failed
        error_message = (
            "I'm unable to answer that question at the moment. Please try again later."
            + (f" (Details: { '; '.join(errors) })" if errors else "")
        )
        metadata = {
            "provider": None,
            "error": True,
            "errors": errors,
        }
        return error_message, metadata

    async def _generate_signals(self, companies: List[tuple]) -> List[Dict[str, Any]]:
        """Generate AI-powered trading signals for companies with high activity."""
        if not companies:
            return []

        # Prepare company data with basic calculations
        company_data = []
        for company_id, ticker, name, trade_count, buy_volume, sell_volume, buy_value, sell_value in companies:
            buy_vol = float(buy_volume or 0)
            sell_vol = float(sell_volume or 0)
            total_vol = buy_vol + sell_vol

            if total_vol == 0:
                continue

            buy_ratio = buy_vol / total_vol if total_vol > 0 else 0
            buy_val = float(buy_value or 0)
            sell_val = float(sell_value or 0)
            total_value = buy_val + sell_val

            company_data.append(
                {
                    "ticker": ticker,
                    "name": name,
                    "trade_count": trade_count,
                    "buy_volume": int(buy_vol),
                    "sell_volume": int(sell_vol),
                    "buy_ratio": round(buy_ratio * 100, 1),  # Already 0-100
                    "total_volume": int(total_vol),
                    "total_value": total_value,
                }
            )

        # Generate AI-powered analysis for signals
        signals_with_ai = await self._add_ai_reasoning_to_signals(company_data)
        return signals_with_ai

    async def _add_ai_reasoning_to_signals(
        self, companies: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Add AI-generated reasoning to trading signals."""
        if not companies:
            return []

        # Format company data for AI
        company_summary = "\n".join(
            [
                f"{c['ticker']} ({c['name']}): {c['trade_count']} trades, "
                f"Buy: {c['buy_volume']:,} shares ({c['buy_ratio']:.1f}%), "
                f"Sell: {c['sell_volume']:,} shares"
                for c in companies
            ]
        )

        system_prompt = """You are an expert financial analyst specializing in insider trading signals.
For each company, provide:
1. Signal: BULLISH, BEARISH, or NEUTRAL
2. Strength: STRONG, MODERATE, or WEAK
3. Reasoning: 1-2 sentence explanation of why this signal makes sense

Consider:
- Buy/sell ratio (>70% buy is bullish, <30% is bearish)
- Volume significance (higher volume = stronger signal)
- Number of insiders participating (more insiders = more conviction)

Return ONLY a JSON array with this exact format:
[
  {
    "ticker": "TSLA",
    "signal": "BULLISH",
    "strength": "STRONG",
    "reasoning": "Extremely high buy ratio of 99.6% with substantial volume indicates strong insider confidence."
  }
]"""

        user_prompt = f"""Analyze these companies and generate trading signals:

{company_summary}

Provide signals in JSON format."""

        try:
            for provider in self._provider_sequence():
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = await self.gemini_client.generate_content_async(
                        full_prompt,
                        generation_config={
                            "temperature": 0.3,
                            "max_output_tokens": 8000,  # Increased for detailed signal analysis
                        },
                    )
                    ai_signals = self._parse_json_response(response.text)
                    if ai_signals and isinstance(ai_signals, list):
                        return self._merge_ai_signals_with_data(companies, ai_signals)
                    break

                if provider == "openai" and self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.3,
                        max_tokens=8000,  # Increased for detailed signal analysis
                        response_format={"type": "json_object"},
                    )
                    ai_signals = self._parse_json_response(
                        response.choices[0].message.content
                    )
                    if ai_signals:
                        return self._merge_ai_signals_with_data(companies, ai_signals)
                    break

        except Exception as e:
            logger.error(f"Error generating AI signals: {e}", exc_info=True)

        # Fallback to rule-based if AI fails
        return self._generate_rule_based_signals(companies)

    def _merge_ai_signals_with_data(
        self, companies: List[Dict], ai_signals: List[Dict]
    ) -> List[Dict]:
        """Merge AI-generated signals with company data."""
        ai_by_ticker = {s.get("ticker"): s for s in ai_signals if s.get("ticker")}

        signals = []
        for company in companies:
            ticker = company["ticker"]
            ai_signal = ai_by_ticker.get(ticker, {})

            # Convert buy_ratio from 0-100 to 0-1 for calculation functions
            buy_ratio_decimal = company["buy_ratio"] / 100 if company["buy_ratio"] else 0
            
            signals.append(
                {
                    "ticker": ticker,
                    "company_name": company["name"],
                    "signal": ai_signal.get(
                        "signal", self._calculate_signal(buy_ratio_decimal)
                    ),
                    "strength": ai_signal.get(
                        "strength", self._calculate_strength(buy_ratio_decimal)
                    ),
                    "trade_count": company["trade_count"],
                    "buy_volume": company["buy_volume"],
                    "sell_volume": company["sell_volume"],
                    "buy_ratio": company["buy_ratio"],  # Keep as 0-100 for frontend
                    "total_value": company.get("total_value", 0),
                    "reasoning": ai_signal.get("reasoning", ""),
                }
            )

        return signals

    def _generate_rule_based_signals(self, companies: List[Dict]) -> List[Dict]:
        """Fallback rule-based signal generation."""
        signals = []
        for company in companies:
            # Convert buy_ratio from 0-100 to 0-1 for calculation functions
            buy_ratio_decimal = company["buy_ratio"] / 100 if company["buy_ratio"] else 0

            signals.append(
                {
                    "ticker": company["ticker"],
                    "company_name": company["name"],
                    "signal": self._calculate_signal(buy_ratio_decimal),
                    "strength": self._calculate_strength(buy_ratio_decimal),
                    "trade_count": company["trade_count"],
                    "buy_volume": company["buy_volume"],
                    "sell_volume": company["sell_volume"],
                    "buy_ratio": company["buy_ratio"],  # Keep as 0-100 for frontend
                    "total_value": company.get("total_value", 0),
                    "reasoning": "",
                }
            )

        return signals

    async def _get_technical_context(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and format technical analysis data for AI prompt.

        Returns dictionary with technical indicators or None if unavailable.
        """
        if not settings.enable_technical_analysis or not settings.yfinance_enabled:
            return None

        try:
            from app.services.market_data_service import MarketDataService

            market_service = MarketDataService()
            technical_data = await market_service.get_technical_indicators(ticker)
            return technical_data
        except Exception as e:
            logger.warning(f"Failed to fetch technical data for {ticker}: {e}")
            return None

    async def _get_fundamental_context(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and format fundamental data for AI prompt.

        Returns dictionary with fundamental metrics or None if unavailable.
        """
        if not settings.enable_fundamental_analysis or not settings.yfinance_enabled:
            return None

        try:
            from app.services.market_data_service import MarketDataService

            market_service = MarketDataService()
            fundamental_data = await market_service.get_fundamental_data(ticker)
            return fundamental_data
        except Exception as e:
            logger.warning(f"Failed to fetch fundamental data for {ticker}: {e}")
            return None

    async def _get_analyst_context(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and format analyst ratings for AI prompt.

        Returns dictionary with analyst consensus or None if unavailable.
        """
        if not settings.enable_analyst_ratings:
            return None

        try:
            from app.services.market_data_service import MarketDataService

            market_service = MarketDataService()
            analyst_data = await market_service.get_analyst_ratings(ticker)
            return analyst_data
        except Exception as e:
            logger.warning(f"Failed to fetch analyst ratings for {ticker}: {e}")
            return None

    async def _get_news_context(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and format news sentiment for AI prompt.

        Returns dictionary with news and sentiment or None if unavailable.
        """
        if not settings.enable_news_sentiment:
            return None

        try:
            from app.services.market_data_service import MarketDataService

            market_service = MarketDataService()
            news_data = await market_service.get_news_sentiment(ticker)
            return news_data
        except Exception as e:
            logger.warning(f"Failed to fetch news sentiment for {ticker}: {e}")
            return None

    def _calculate_signal(self, buy_ratio: float) -> str:
        """Calculate signal from buy ratio."""
        if buy_ratio > 0.7:
            return "BULLISH"
        elif buy_ratio < 0.3:
            return "BEARISH"
        return "NEUTRAL"

    def _calculate_strength(self, buy_ratio: float) -> str:
        """Calculate strength from buy ratio."""
        if buy_ratio > 0.85 or buy_ratio < 0.15:
            return "STRONG"
        elif buy_ratio > 0.7 or buy_ratio < 0.3:
            return "MODERATE"
        return "WEAK"
