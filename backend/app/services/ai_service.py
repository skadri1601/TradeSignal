"""
AI Service for TradeSignal.

Provides AI-powered insights using OpenAI's GPT models.
Analyzes insider trading patterns and generates natural language summaries.
"""

import logging
import json
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
    - Google Gemini 1.5 Flash (default - cheap, fast, 1M context)
    - OpenAI GPT-4o-mini (fallback - reliable, structured output)

    Features:
    - Analyze company trading patterns
    - Generate daily summaries
    - Answer natural language queries
    - Provide trading signals
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
        self,
        ticker: str,
        days_back: int = 30
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
                        Trade.company_id == company.id,
                        Trade.filing_date >= cutoff_date
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
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Prepare trade data for AI
            trade_summary = self._format_trades_for_ai(trades_with_insiders, company)

            # Generate AI analysis
            analysis = await self._generate_company_analysis(
                company.name,
                ticker,
                trade_summary,
                days_back
            )

            return {
                "ticker": ticker,
                "company_name": company.name,
                "days_analyzed": days_back,
                "total_trades": len(trades_with_insiders),
                 "timestamp": datetime.utcnow().isoformat(),
                **analysis
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
            # Get trades from last 7 days
            cutoff_date = datetime.utcnow() - timedelta(days=7)

            result = await self.db.execute(
                select(Trade, Company, Insider)
                .join(Company, Trade.company_id == Company.id)
                .join(Insider, Trade.insider_id == Insider.id)
                .where(Trade.filing_date >= cutoff_date)
                .order_by(Trade.filing_date.desc())
            )
            trades_data = result.all()

            if not trades_data:
                return {
                    "company_summaries": [],
                    "total_trades": 0,
                    "generated_at": datetime.utcnow().isoformat(),
                    "period": "last 7 days"
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
                        "insiders": set()
                    }

                trade_value = self._get_trade_value(trade)
                companies_map[ticker]["trades"].append({
                    "insider": insider.name,
                    "role": insider.title or "Insider",
                    "type": trade.transaction_type,
                    "shares": self._get_trade_shares(trade),
                    "value": trade_value,
                    "date": trade.filing_date.isoformat()
                })
                companies_map[ticker]["total_value"] += trade_value
                companies_map[ticker]["insiders"].add(insider.name)
                if trade.transaction_type == "BUY":
                    companies_map[ticker]["buy_count"] += 1
                else:
                    companies_map[ticker]["sell_count"] += 1

            # Sort companies by total trade value - show top 10 to stay within free API limits
            sorted_companies = sorted(
                companies_map.values(),
                key=lambda x: x["total_value"],
                reverse=True
            )[:10]  # Top 10 companies (optimized for Gemini free tier)

            # Generate AI summary for each company
            company_summaries = []
            for company_data in sorted_companies:
                # Convert set to list for JSON serialization
                company_data["insiders"] = list(company_data["insiders"])

                summary = await self._generate_company_news_summary(company_data)
                company_summaries.append({
                    "ticker": company_data["ticker"],
                    "company_name": company_data["company_name"],
                    "summary": summary,
                    "total_value": company_data["total_value"],
                    "trade_count": len(company_data["trades"]),
                    "buy_count": company_data["buy_count"],
                    "sell_count": company_data["sell_count"],
                    "insider_count": len(company_data["insiders"]),
                    "latest_date": company_data["trades"][0]["date"]
                })

            return {
                "company_summaries": company_summaries,
                "total_trades": len(trades_data),
                "generated_at": datetime.utcnow().isoformat(),
                "period": "last 7 days"
            }

        except Exception as e:
            logger.error(f"Error generating daily summary: {e}", exc_info=True)
            return {"error": str(e)}

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
            answer = await self._generate_chatbot_response(question, stats)

            return {
                "question": question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat()
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
            cutoff_date = datetime.utcnow() - timedelta(days=7)

            # Group trades by company
            result = await self.db.execute(
                select(
                    Company.id,
                    Company.ticker,
                    Company.name,
                    func.count(Trade.id).label("trade_count"),
                    func.sum(
                        case(
                            (Trade.transaction_type == "BUY", Trade.shares),
                            else_=0
                        )
                    ).label("buy_volume"),
                    func.sum(
                        case(
                            (Trade.transaction_type == "SELL", Trade.shares),
                            else_=0
                        )
                    ).label("sell_volume")
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
                    "period": "7 days"
                }

            # Generate signals
            signals = await self._generate_signals(companies)

            return {
                "signals": signals,
                "generated_at": datetime.utcnow().isoformat(),
                "period": "7 days"
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

    @staticmethod
    def _get_trade_value(trade: Trade) -> float:
        """Return trade value using stored total or calculated fallback."""
        total_value = getattr(trade, "total_value", None)
        if total_value is not None:
            return float(total_value)

        shares = getattr(trade, "shares", None)
        price = getattr(trade, "price_per_share", None)
        if shares is not None and price is not None:
            return float(shares * price)

        return 0.0

    def _format_trades_for_ai(
        self,
        trades_with_insiders: List[tuple],
        company: Company
    ) -> str:
        """Format trades into a summary for AI analysis."""
        buy_trades = []
        sell_trades = []
        total_buy_value = 0
        total_sell_value = 0

        for trade, insider in trades_with_insiders:
            shares = self._get_trade_shares(trade)
            value = self._get_trade_value(trade)
            trade_info = {
                "insider": insider.name,
                "role": insider.title or "Insider",
                "shares": shares,
                "value": value,
                "date": trade.filing_date.strftime("%Y-%m-%d")
            }

            if trade.transaction_type == "BUY":
                buy_trades.append(trade_info)
                total_buy_value += trade_info["value"]
            else:
                sell_trades.append(trade_info)
                total_sell_value += trade_info["value"]

        summary = f"Company: {company.name} ({company.ticker})\n\n"
        summary += f"Total Buy Trades: {len(buy_trades)} (${total_buy_value:,.0f})\n"
        summary += f"Total Sell Trades: {len(sell_trades)} (${total_sell_value:,.0f})\n\n"

        if buy_trades:
            summary += "Recent BUY Trades:\n"
            for t in buy_trades[:5]:
                summary += f"- {t['insider']} ({t['role']}): {t['shares']:,.0f} shares, ${t['value']:,.0f} on {t['date']}\n"

        if sell_trades:
            summary += "\nRecent SELL Trades:\n"
            for t in sell_trades[:5]:
                summary += f"- {t['insider']} ({t['role']}): {t['shares']:,.0f} shares, ${t['value']:,.0f} on {t['date']}\n"

        return summary

    async def _generate_company_news_summary(self, company_data: Dict) -> str:
        """Generate a news-style summary for a single company's insider trading activity."""
        system_prompt = """You are a financial news writer specializing in insider trading.
Write a concise, news-style summary (2-3 sentences) about this company's recent insider activity.

Focus on:
- What insiders are doing (buying vs selling)
- Who is involved (executives, directors)
- The significance (large values, unusual patterns)

Write in an engaging, journalistic style like Bloomberg or CNBC. Be factual but highlight what's noteworthy."""

        user_prompt = f"""Write a news summary for {company_data['company_name']} ({company_data['ticker']}):

ACTIVITY:
- Total trades: {len(company_data['trades'])}
- Buy transactions: {company_data['buy_count']}
- Sell transactions: {company_data['sell_count']}
- Total value: ${company_data['total_value']:,.0f}
- Unique insiders: {len(company_data['insiders'])}

INSIDERS INVOLVED:
{', '.join(company_data['insiders'][:5])}

Write a 2-3 sentence news summary highlighting the most important aspects."""

        # Call AI directly
        errors = []
        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = await self.gemini_client.generate_content_async(
                        full_prompt,
                        generation_config={
                            "temperature": 0.7,
                            "max_output_tokens": 200,
                        }
                    )
                    return response.text.strip()

                if provider == "openai" and self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"AI error generating company summary ({provider}): {e}")
                errors.append(str(e))
                continue

        # Fallback if AI fails
        sentiment = "buying" if company_data['buy_count'] > company_data['sell_count'] else "selling"
        return f"{company_data['ticker']} insiders showed {sentiment} activity with {len(company_data['trades'])} transactions totaling ${company_data['total_value']:,.0f}."

    async def _generate_company_analysis(
        self,
        company_name: str,
        ticker: str,
        trade_summary: str,
        days_back: int
    ) -> Dict[str, Any]:
        """Generate deep AI-powered analysis for a company."""
        system_prompt = """You are a senior financial analyst and insider trading expert with deep market knowledge.

Provide a comprehensive analysis with:
1. **Analysis**: 3-4 sentence analytical summary going beyond surface-level observations. Identify patterns, anomalies, and implications.

2. **Sentiment**: BULLISH, BEARISH, or NEUTRAL based on holistic assessment

3. **Key Insights** (4-6 bullet points):
   - Identify specific patterns (clustering, timing, unusual behavior)
   - Highlight significant insiders and their roles
   - Compare transaction sizes to historical norms if notable
   - Note any coordinated activity or changes in behavior
   - Assess potential motivations (tax planning, liquidity needs, conviction)
   - Provide actionable intelligence for investors

Be analytical, not descriptive. Focus on "why" and "what it means", not just "what happened".
Consider the broader context: insider roles, transaction sizes, timing, patterns, and market implications.

Respond ONLY in this exact JSON format:
{
  "analysis": "your detailed analytical summary",
  "sentiment": "BULLISH|BEARISH|NEUTRAL",
  "insights": ["insight 1", "insight 2", "insight 3", "insight 4"]
}"""

        user_prompt = f"""Provide a deep analysis of insider trading activity for {company_name} ({ticker}) over the past {days_back} days:

{trade_summary}

Remember: Be analytical and insightful, not just descriptive. What do these trades really tell us?"""

        errors: List[str] = []

        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = await self.gemini_client.generate_content_async(
                        full_prompt,
                        generation_config={
                            "temperature": settings.ai_temperature,
                            "max_output_tokens": settings.ai_max_tokens,
                        }
                    )
                    parsed = self._parse_json_response(response.text)
                    if parsed is None:
                        raise ValueError("Gemini response was not valid JSON")
                    self.provider = provider
                    return parsed

                if provider == "openai" and self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=settings.ai_temperature,
                        max_tokens=settings.ai_max_tokens,
                        response_format={"type": "json_object"}
                    )
                    parsed = self._parse_json_response(response.choices[0].message.content)
                    if parsed is None:
                        raise ValueError("OpenAI response was not valid JSON")
                    self.provider = provider
                    return parsed
            except Exception as e:
                logger.error(f"AI API error ({provider}): {e}", exc_info=True)
                errors.append(f"{provider}: {e}")
                continue

        return {
            "analysis": "Unable to generate AI analysis at this time.",
            "sentiment": "NEUTRAL",
            "insights": [],
            "error": "; ".join(errors) if errors else "No AI provider available"
        }

    async def _generate_daily_summary(
        self,
        top_trades: List[Dict],
        total_count: int
    ) -> str:
        """Generate daily summary text with rich AI-powered insights."""
        system_prompt = """You are an expert financial analyst specializing in insider trading analysis.
Write an insightful daily summary that goes beyond simple facts. Consider:
- Transaction patterns (clustering, timing, unusual activity)
- Insider roles and their significance (C-suite vs directors)
- Trade sizes relative to typical activity
- Sector trends or concentrations
- Potential market implications

Be concise (4-5 sentences) but analytical. Use professional yet engaging language that provides real value to investors."""

        # Enrich trade data with context
        trades_by_company = {}
        total_buy_value = 0
        total_sell_value = 0
        c_suite_trades = []

        for t in top_trades:
            ticker = t['ticker']
            if ticker not in trades_by_company:
                trades_by_company[ticker] = {'buy': 0, 'sell': 0, 'insiders': []}

            if t['type'] == 'BUY':
                total_buy_value += t['value']
                trades_by_company[ticker]['buy'] += t['value']
            else:
                total_sell_value += t['value']
                trades_by_company[ticker]['sell'] += t['value']

            role = t['role'].upper()
            if any(title in role for title in ['CEO', 'CFO', 'COO', 'PRESIDENT', 'CHIEF']):
                c_suite_trades.append(f"{t['ticker']} {t['insider']} ({t['role']})")

            trades_by_company[ticker]['insiders'].append(t['insider'])

        # Calculate insights
        buy_sell_ratio = (total_buy_value / total_sell_value * 100) if total_sell_value > 0 else 100
        companies_with_activity = len(trades_by_company)

        # Format detailed trade information
        trades_text = "\n".join([
            f"{t['ticker']} - {t['company']}: {t['insider']} ({t['role']}) {t['type']} "
            f"{t['shares']:,.0f} shares @ ${t['value']:,.0f} on {t['date']}"
            for t in top_trades[:10]
        ])

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

Write a 4-5 sentence analysis that identifies patterns, highlights significant trades, and provides actionable insights for investors."""

        errors: List[str] = []

        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = await self.gemini_client.generate_content_async(
                        full_prompt,
                        generation_config={
                            "temperature": settings.ai_temperature,
                            "max_output_tokens": 300,
                        }
                    )
                    self.provider = provider
                    return response.text.strip()

                if provider == "openai" and self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=settings.ai_temperature,
                        max_tokens=300
                    )
                    self.provider = provider
                    return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"AI API error ({provider}): {e}", exc_info=True)
                errors.append(f"{provider}: {e}")
                continue

        highlighted = [trade["ticker"] for trade in top_trades[:2] if trade.get("ticker")]
        if highlighted:
            joined = " and ".join(highlighted) if len(highlighted) > 1 else highlighted[0]
            return (
                f"Today saw {total_count} insider trades, including notable activity in {joined}. "
                f"(AI unavailable: { '; '.join(errors) if errors else 'no provider' })"
            )
        return f"Today saw {total_count} insider trades. (AI unavailable: { '; '.join(errors) if errors else 'no provider' })"

    @staticmethod
    def _parse_json_response(raw_text: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse JSON returned by AI providers, handling fenced blocks."""
        if not raw_text:
            return None

        text = raw_text.strip()
        lower_text = text.lower()
        for fence in ("```json", "```"):
            if lower_text.startswith(fence):
                text = text[len(fence):].strip()
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
                func.sum(
                    case(
                        (Trade.transaction_type == "BUY", 1),
                        else_=0
                    )
                ).label("buy_trades"),
                func.sum(
                    case(
                        (Trade.transaction_type == "SELL", 1),
                        else_=0
                    )
                ).label("sell_trades")
            )
            .where(Trade.filing_date >= cutoff_date)
        )
        stats = result.first()

        return {
            "total_trades": stats.total_trades or 0,
            "buy_trades": stats.buy_trades or 0,
            "sell_trades": stats.sell_trades or 0,
            "period_days": 30
        }

    async def _generate_chatbot_response(
        self,
        question: str,
        stats: Dict[str, Any]
    ) -> str:
        """Generate intelligent, context-aware chatbot responses with real data."""
        buy_sell_ratio = (stats['buy_trades'] / max(stats['sell_trades'], 1)) * 100
        market_sentiment = "bullish" if buy_sell_ratio > 60 else "bearish" if buy_sell_ratio < 40 else "neutral"

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
                    case(
                        (Trade.transaction_type == "BUY", Trade.total_value),
                        else_=0
                    )
                ).label("total_buy_value")
            )
            .join(Trade, Company.id == Trade.company_id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
            .where(Trade.transaction_type == "BUY")
            .group_by(Company.ticker, Company.name, Insider.name, Insider.relationship)
            .order_by(func.sum(case((Trade.transaction_type == "BUY", Trade.total_value), else_=0)).desc())
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
                    case(
                        (Trade.transaction_type == "SELL", Trade.total_value),
                        else_=0
                    )
                ).label("total_sell_value")
            )
            .join(Trade, Company.id == Trade.company_id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
            .where(Trade.transaction_type == "SELL")
            .group_by(Company.ticker, Company.name, Insider.name, Insider.relationship)
            .order_by(func.sum(case((Trade.transaction_type == "SELL", Trade.total_value), else_=0)).desc())
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
                func.sum(Trade.total_value).label("total_value")
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
                func.sum(case((Trade.transaction_type == "BUY", 1), else_=0)).label("buy_count"),
                func.sum(case((Trade.transaction_type == "SELL", 1), else_=0)).label("sell_count")
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
                func.count(Trade.id).label("trade_count")
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
        all_companies_list = ", ".join([row.ticker for row in all_companies[:50]])  # Show first 50
        if len(all_companies) > 50:
            all_companies_list += f" (and {len(all_companies) - 50} more)"

        if top_buyers:
            top_buyers_list = "\n".join([
                f"- {row.ticker}: {row.insider_name} ({row.relationship or 'Insider'}) - {row.buy_count} buys, {format_value(row.total_buy_value)}"
                for row in top_buyers[:10]
            ])
        else:
            top_buyers_list = "No significant insider buying activity in the last 30 days."

        if top_sellers:
            top_sellers_list = "\n".join([
                f"- {row.ticker}: {row.insider_name} ({row.relationship or 'Insider'}) - {row.sell_count} sells, {format_value(row.total_sell_value)}"
                for row in top_sellers[:10]
            ])
        else:
            top_sellers_list = "No significant insider selling activity in the last 30 days."

        # Format top insiders by share volume
        if top_insiders_volume:
            top_insiders_list = "\n".join([
                f"- {row.ticker}: {row.insider_name} ({row.relationship or 'Insider'}) - {row.total_shares:,.0f} shares, {format_value(row.total_value)}"
                for row in top_insiders_volume[:15]  # Show top 15
            ])
        else:
            top_insiders_list = "No insider buying activity in the last 30 days."

        # Format most active insiders
        if most_active_insiders:
            most_active_list = "\n".join([
                f"- {row.ticker}: {row.insider_name} ({row.relationship or 'Insider'}) - {row.trade_count} trades ({row.buy_count} buys, {row.sell_count} sells)"
                for row in most_active_insiders[:10]  # Show top 10
            ])
        else:
            most_active_list = "No active insiders in the last 30 days."

        # Format insider role distribution
        if insider_roles:
            insider_roles_list = "\n".join([
                f"- {row.relationship}: {row.insider_count} insiders, {row.trade_count} trades"
                for row in insider_roles[:10]  # Show top 10 roles
            ])
        else:
            insider_roles_list = "No insider role data available."

        system_prompt = f"""You are TradeSignal's AI analyst with COMPLETE DATABASE ACCESS to ALL {len(all_companies)} companies with insider trading activity.

DATABASE COVERAGE (Last 30 Days):
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

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:
1. You have access to data from ALL {len(all_companies)} companies listed above
2. You have data on ALL INSIDER ROLES: CEOs, CFOs, Directors, Officers, 10% Owners, Presidents, VPs, etc.
3. The "top" lists are just examples - you can query any company or insider from the full database
4. When asked about "biggest trades", cite the SPECIFIC INSIDERS and their ROLES from the lists above
5. Format: "[Insider Name] ([Title/Role]) at [Ticker] bought/sold [amount]"
6. If a value shows "Not Disclosed", explain the SEC filing didn't include the value
7. NEVER say "I'm not sure" - you have complete database access
8. Be PRECISE and CONFIDENT - this is real SEC Form 4 data
9. When discussing insiders, mention their specific roles (CEO, CFO, Director, etc.) to provide context
10. Use the insider role distribution to provide insights about which types of insiders are most active

Answer using this real-time data from the complete insider trading database."""

        errors: List[str] = []

        for provider in self._provider_sequence():
            try:
                if provider == "gemini" and self.gemini_client:
                    full_prompt = f"{system_prompt}\n\nUser question: {question}"
                    response = await self.gemini_client.generate_content_async(
                        full_prompt,
                        generation_config={
                            "temperature": 0.2,  # Very low temperature for maximum precision
                            "max_output_tokens": 500,
                        }
                    )
                    self.provider = provider
                    return response.text.strip()

                if provider == "openai" and self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question}
                        ],
                        temperature=0.2,  # Very low temperature for maximum precision
                        max_tokens=500
                    )
                    self.provider = provider
                    return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"AI API error ({provider}): {e}", exc_info=True)
                errors.append(f"{provider}: {e}")
                continue

        return "I'm unable to answer that question at the moment. Please try again later." + (
            f" (Details: { '; '.join(errors) })" if errors else ""
        )

    async def _generate_signals(self, companies: List[tuple]) -> List[Dict[str, Any]]:
        """Generate AI-powered trading signals for companies with high activity."""
        if not companies:
            return []

        # Prepare company data with basic calculations
        company_data = []
        for company_id, ticker, name, trade_count, buy_volume, sell_volume in companies:
            buy_vol = float(buy_volume or 0)
            sell_vol = float(sell_volume or 0)
            total_vol = buy_vol + sell_vol

            if total_vol == 0:
                continue

            buy_ratio = buy_vol / total_vol if total_vol > 0 else 0

            company_data.append({
                "ticker": ticker,
                "name": name,
                "trade_count": trade_count,
                "buy_volume": int(buy_vol),
                "sell_volume": int(sell_vol),
                "buy_ratio": round(buy_ratio * 100, 1),
                "total_volume": int(total_vol)
            })

        # Generate AI-powered analysis for signals
        signals_with_ai = await self._add_ai_reasoning_to_signals(company_data)
        return signals_with_ai

    async def _add_ai_reasoning_to_signals(self, companies: List[Dict]) -> List[Dict[str, Any]]:
        """Add AI-generated reasoning to trading signals."""
        if not companies:
            return []

        # Format company data for AI
        company_summary = "\n".join([
            f"{c['ticker']} ({c['name']}): {c['trade_count']} trades, "
            f"Buy: {c['buy_volume']:,} shares ({c['buy_ratio']:.1f}%), "
            f"Sell: {c['sell_volume']:,} shares"
            for c in companies
        ])

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
                            "max_output_tokens": 2000,
                        }
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
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=2000,
                        response_format={"type": "json_object"}
                    )
                    ai_signals = self._parse_json_response(response.choices[0].message.content)
                    if ai_signals:
                        return self._merge_ai_signals_with_data(companies, ai_signals)
                    break

        except Exception as e:
            logger.error(f"Error generating AI signals: {e}", exc_info=True)

        # Fallback to rule-based if AI fails
        return self._generate_rule_based_signals(companies)

    def _merge_ai_signals_with_data(self, companies: List[Dict], ai_signals: List[Dict]) -> List[Dict]:
        """Merge AI-generated signals with company data."""
        ai_by_ticker = {s.get('ticker'): s for s in ai_signals if s.get('ticker')}

        signals = []
        for company in companies:
            ticker = company['ticker']
            ai_signal = ai_by_ticker.get(ticker, {})

            signals.append({
                "ticker": ticker,
                "company_name": company['name'],
                "signal": ai_signal.get('signal', self._calculate_signal(company['buy_ratio'])),
                "strength": ai_signal.get('strength', self._calculate_strength(company['buy_ratio'])),
                "trade_count": company['trade_count'],
                "buy_volume": company['buy_volume'],
                "sell_volume": company['sell_volume'],
                "buy_ratio": company['buy_ratio'],
                "reasoning": ai_signal.get('reasoning', '')
            })

        return signals

    def _generate_rule_based_signals(self, companies: List[Dict]) -> List[Dict]:
        """Fallback rule-based signal generation."""
        signals = []
        for company in companies:
            buy_ratio = company['buy_ratio'] / 100

            signals.append({
                "ticker": company['ticker'],
                "company_name": company['name'],
                "signal": self._calculate_signal(buy_ratio),
                "strength": self._calculate_strength(buy_ratio),
                "trade_count": company['trade_count'],
                "buy_volume": company['buy_volume'],
                "sell_volume": company['sell_volume'],
                "buy_ratio": company['buy_ratio'],
                "reasoning": ""
            })

        return signals

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
