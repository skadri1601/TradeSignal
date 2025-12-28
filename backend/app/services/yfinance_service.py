"""
yfinance Data Service

Fetches stock data from Yahoo Finance via yfinance library.
No rate limits, but use caching to reduce load.
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
import asyncio

import yfinance as yf
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.market_data import (
    DividendHistory,
    EarningsCalendar,
    AnalystRecommendation,
    FinancialStatement,
)

logger = logging.getLogger(__name__)


class YFinanceService:
    """
    Service for fetching data from yfinance.

    All methods are async-compatible but yfinance itself is sync.
    Data is cached in database to avoid redundant API calls.
    """

    # Cache TTLs in hours
    DIVIDENDS_TTL_HOURS = 24
    EARNINGS_TTL_HOURS = 6
    RECOMMENDATIONS_TTL_HOURS = 6
    FINANCIALS_TTL_HOURS = 24

    async def get_dividends(
        self,
        db: AsyncSession,
        ticker: str,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get dividend history for a stock.

        Args:
            db: Database session
            ticker: Stock ticker symbol
            force_refresh: Force fetch from yfinance

        Returns:
            List of dividend records
        """
        company = await self._get_company(db, ticker)
        if not company:
            return []

        # Check cache
        if not force_refresh:
            cached = await self._get_cached_dividends(db, company.id)
            if cached:
                return cached

        # Fetch from yfinance (run in thread pool since it's sync)
        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, lambda: yf.Ticker(ticker))
            dividends = await loop.run_in_executor(None, lambda: stock.dividends)

            if dividends.empty:
                return []

            # Clear old data and insert new
            await db.execute(
                delete(DividendHistory).where(DividendHistory.company_id == company.id)
            )

            records = []
            for ex_date, amount in dividends.items():
                div = DividendHistory(
                    company_id=company.id,
                    ex_date=ex_date.date() if hasattr(ex_date, 'date') else ex_date,
                    amount=Decimal(str(amount)),
                )
                db.add(div)
                ex_date_obj = ex_date.date() if hasattr(ex_date, 'date') else ex_date
                records.append({
                    "ex_date": ex_date_obj.isoformat() if isinstance(ex_date_obj, date) else str(ex_date_obj),
                    "amount": float(amount),
                })

            await db.commit()
            logger.info(f"Fetched {len(records)} dividends for {ticker}")
            return records

        except Exception as e:
            logger.error(f"Error fetching dividends for {ticker}: {e}", exc_info=True)
            await db.rollback()
            return []

    async def get_earnings_calendar(
        self,
        db: AsyncSession,
        ticker: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get earnings calendar (next earnings date, estimates).

        Returns:
            Dict with earnings_date, eps_estimate, revenue_estimate
        """
        company = await self._get_company(db, ticker)
        if not company:
            return {}

        # Check cache
        if not force_refresh:
            cached = await self._get_cached_earnings(db, company.id)
            if cached:
                return cached

        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, lambda: yf.Ticker(ticker))
            calendar = await loop.run_in_executor(None, lambda: stock.calendar)

            if calendar is None or calendar.empty:
                return {}

            # Extract data - calendar is a DataFrame with dates as index
            result = {}

            if hasattr(calendar, 'T'):
                cal_dict = calendar.T.to_dict()
                if cal_dict:
                    first_key = list(cal_dict.keys())[0]
                    data = cal_dict[first_key]

                    earnings_date = data.get('Earnings Date')
                    if earnings_date:
                        if hasattr(earnings_date, 'date'):
                            result['earnings_date'] = earnings_date.date().isoformat()
                        else:
                            result['earnings_date'] = str(earnings_date)

                    result['eps_estimate'] = float(data.get('EPS Estimate', 0)) if data.get('EPS Estimate') is not None else None
                    result['revenue_estimate'] = float(data.get('Revenue Estimate', 0)) if data.get('Revenue Estimate') is not None else None

            # Save to database
            if result.get('earnings_date'):
                await self._save_earnings_calendar(db, company.id, result)

            return result

        except Exception as e:
            logger.error(f"Error fetching earnings calendar for {ticker}: {e}", exc_info=True)
            return {}

    async def get_analyst_recommendations(
        self,
        db: AsyncSession,
        ticker: str,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get analyst recommendations history.

        Returns:
            List of recommendation periods with buy/hold/sell counts
        """
        company = await self._get_company(db, ticker)
        if not company:
            return []

        # Check cache
        if not force_refresh:
            cached = await self._get_cached_recommendations(db, company.id)
            if cached:
                return cached

        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, lambda: yf.Ticker(ticker))
            recommendations = await loop.run_in_executor(None, lambda: stock.recommendations)

            if recommendations is None or recommendations.empty:
                return []

            # Clear old data
            await db.execute(
                delete(AnalystRecommendation).where(
                    AnalystRecommendation.company_id == company.id
                )
            )

            records = []
            for idx, row in recommendations.iterrows():
                period_date = idx.date() if hasattr(idx, 'date') else date.today()
                rec = AnalystRecommendation(
                    company_id=company.id,
                    period=period_date,
                    strong_buy=int(row.get('strongBuy', 0) or 0),
                    buy=int(row.get('buy', 0) or 0),
                    hold=int(row.get('hold', 0) or 0),
                    sell=int(row.get('sell', 0) or 0),
                    strong_sell=int(row.get('strongSell', 0) or 0),
                )
                db.add(rec)
                records.append({
                    "period": rec.period.isoformat(),
                    "strong_buy": rec.strong_buy,
                    "buy": rec.buy,
                    "hold": rec.hold,
                    "sell": rec.sell,
                    "strong_sell": rec.strong_sell,
                })

            await db.commit()
            logger.info(f"Fetched {len(records)} recommendations for {ticker}")
            return records[-12:] if records else []  # Last 12 months

        except Exception as e:
            logger.error(f"Error fetching recommendations for {ticker}: {e}", exc_info=True)
            await db.rollback()
            return []

    async def get_financial_statements(
        self,
        db: AsyncSession,
        ticker: str,
        statement_type: str = "income",  # 'income', 'balance', 'cashflow'
        period: str = "quarterly",  # 'quarterly', 'annual'
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get financial statements.

        Args:
            statement_type: 'income', 'balance', or 'cashflow'
            period: 'quarterly' or 'annual'

        Returns:
            List of statement periods with financial data
        """
        company = await self._get_company(db, ticker)
        if not company:
            return []

        # Check cache
        if not force_refresh:
            cached = await self._get_cached_financials(
                db, company.id, statement_type, period
            )
            if cached:
                return cached

        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, lambda: yf.Ticker(ticker))

            # Get the appropriate statement
            if statement_type == "income":
                df = await loop.run_in_executor(
                    None,
                    lambda: stock.quarterly_income_stmt if period == "quarterly" else stock.income_stmt
                )
            elif statement_type == "balance":
                df = await loop.run_in_executor(
                    None,
                    lambda: stock.quarterly_balance_sheet if period == "quarterly" else stock.balance_sheet
                )
            elif statement_type == "cashflow":
                df = await loop.run_in_executor(
                    None,
                    lambda: stock.quarterly_cashflow if period == "quarterly" else stock.cashflow
                )
            else:
                return []

            if df is None or df.empty:
                return []

            # Clear old data for this type/period
            await db.execute(
                delete(FinancialStatement).where(
                    FinancialStatement.company_id == company.id,
                    FinancialStatement.statement_type == statement_type,
                    FinancialStatement.period_type == period,
                )
            )

            records = []
            for col in df.columns:
                period_end = col.date() if hasattr(col, 'date') else date.today()

                # Convert DataFrame column to dict, handling NaN
                data = {}
                for idx, value in df[col].items():
                    if value is not None and str(value) != 'nan':
                        try:
                            data[str(idx)] = float(value) if isinstance(value, (int, float)) else str(value)
                        except (ValueError, TypeError):
                            data[str(idx)] = str(value)

                stmt = FinancialStatement(
                    company_id=company.id,
                    period_type=period,
                    period_end=period_end,
                    statement_type=statement_type,
                    data=data,
                )
                db.add(stmt)
                records.append({
                    "period_end": period_end.isoformat() if isinstance(period_end, date) else str(period_end),
                    "data": data,
                })

            await db.commit()
            logger.info(f"Fetched {len(records)} {statement_type} statements for {ticker}")
            return records

        except Exception as e:
            logger.error(f"Error fetching {statement_type} for {ticker}: {e}", exc_info=True)
            await db.rollback()
            return []

    # Helper methods

    async def _get_company(self, db: AsyncSession, ticker: str) -> Optional[Company]:
        """Get company by ticker."""
        result = await db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()

    async def _get_cached_dividends(
        self, db: AsyncSession, company_id: int
    ) -> Optional[List[Dict]]:
        """Check if we have recent cached dividends."""
        result = await db.execute(
            select(DividendHistory)
            .where(DividendHistory.company_id == company_id)
            .order_by(DividendHistory.ex_date.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if latest and latest.created_at:
            age = datetime.utcnow() - latest.created_at
            if age.total_seconds() < self.DIVIDENDS_TTL_HOURS * 3600:
                # Return all cached dividends
                all_divs = await db.execute(
                    select(DividendHistory)
                    .where(DividendHistory.company_id == company_id)
                    .order_by(DividendHistory.ex_date.desc())
                )
                return [
                    {"ex_date": d.ex_date.isoformat(), "amount": float(d.amount)}
                    for d in all_divs.scalars()
                ]
        return None

    async def _get_cached_earnings(
        self, db: AsyncSession, company_id: int
    ) -> Optional[Dict]:
        """Check for cached earnings calendar."""
        result = await db.execute(
            select(EarningsCalendar)
            .where(EarningsCalendar.company_id == company_id)
            .order_by(EarningsCalendar.earnings_date.desc())
            .limit(1)
        )
        earnings = result.scalar_one_or_none()

        if earnings and earnings.updated_at:
            age = datetime.utcnow() - earnings.updated_at
            if age.total_seconds() < self.EARNINGS_TTL_HOURS * 3600:
                return {
                    "earnings_date": earnings.earnings_date.isoformat(),
                    "eps_estimate": float(earnings.eps_estimate) if earnings.eps_estimate else None,
                    "revenue_estimate": float(earnings.revenue_estimate) if earnings.revenue_estimate else None,
                }
        return None

    async def _get_cached_recommendations(
        self, db: AsyncSession, company_id: int
    ) -> Optional[List[Dict]]:
        """Check for cached recommendations."""
        result = await db.execute(
            select(AnalystRecommendation)
            .where(AnalystRecommendation.company_id == company_id)
            .order_by(AnalystRecommendation.period.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if latest and latest.updated_at:
            age = datetime.utcnow() - latest.updated_at
            if age.total_seconds() < self.RECOMMENDATIONS_TTL_HOURS * 3600:
                all_recs = await db.execute(
                    select(AnalystRecommendation)
                    .where(AnalystRecommendation.company_id == company_id)
                    .order_by(AnalystRecommendation.period.desc())
                    .limit(12)
                )
                return [
                    {
                        "period": r.period.isoformat(),
                        "strong_buy": r.strong_buy,
                        "buy": r.buy,
                        "hold": r.hold,
                        "sell": r.sell,
                        "strong_sell": r.strong_sell,
                    }
                    for r in all_recs.scalars()
                ]
        return None

    async def _get_cached_financials(
        self,
        db: AsyncSession,
        company_id: int,
        statement_type: str,
        period_type: str
    ) -> Optional[List[Dict]]:
        """Check for cached financial statements."""
        result = await db.execute(
            select(FinancialStatement)
            .where(
                FinancialStatement.company_id == company_id,
                FinancialStatement.statement_type == statement_type,
                FinancialStatement.period_type == period_type,
            )
            .order_by(FinancialStatement.period_end.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if latest and latest.updated_at:
            age = datetime.utcnow() - latest.updated_at
            if age.total_seconds() < self.FINANCIALS_TTL_HOURS * 3600:
                all_stmts = await db.execute(
                    select(FinancialStatement)
                    .where(
                        FinancialStatement.company_id == company_id,
                        FinancialStatement.statement_type == statement_type,
                        FinancialStatement.period_type == period_type,
                    )
                    .order_by(FinancialStatement.period_end.desc())
                )
                return [
                    {"period_end": s.period_end.isoformat(), "data": s.data}
                    for s in all_stmts.scalars()
                ]
        return None

    async def _save_earnings_calendar(
        self, db: AsyncSession, company_id: int, data: Dict
    ) -> None:
        """Save earnings calendar to database."""
        earnings_date = data.get('earnings_date')
        if not earnings_date:
            return

        if isinstance(earnings_date, str):
            earnings_date = datetime.strptime(earnings_date, "%Y-%m-%d").date()

        # Upsert
        result = await db.execute(
            select(EarningsCalendar)
            .where(
                EarningsCalendar.company_id == company_id,
                EarningsCalendar.earnings_date == earnings_date,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.eps_estimate = Decimal(str(data.get('eps_estimate'))) if data.get('eps_estimate') else None
            existing.revenue_estimate = Decimal(str(data.get('revenue_estimate'))) if data.get('revenue_estimate') else None
            existing.updated_at = datetime.utcnow()
        else:
            ec = EarningsCalendar(
                company_id=company_id,
                earnings_date=earnings_date,
                eps_estimate=Decimal(str(data.get('eps_estimate'))) if data.get('eps_estimate') else None,
                revenue_estimate=Decimal(str(data.get('revenue_estimate'))) if data.get('revenue_estimate') else None,
            )
            db.add(ec)

        await db.commit()

