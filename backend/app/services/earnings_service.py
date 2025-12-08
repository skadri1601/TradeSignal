"""
Earnings Service

Fetches and tracks earnings announcements, estimates, and actual results
for all companies in the database.

Data Sources:
- Yahoo Finance (earnings calendar)
- Alpha Vantage (earnings data)
- Finnhub (earnings calendar)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Company
import yfinance as yf
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class EarningsService:
    """
    Service for fetching and managing earnings data.

    Tracks:
    - Upcoming earnings dates
    - Earnings estimates vs actual
    - Earnings history
    - Earnings surprises
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def get_company_earnings(
        self, ticker: str, quarters: int = 8
    ) -> Dict[str, Any]:
        """
        Get earnings data for a specific company.

        Args:
            ticker: Company ticker symbol
            quarters: Number of quarters to fetch (default: 8 = 2 years)

        Returns:
            Dict with earnings history, upcoming dates, estimates
        """
        try:
            # Get company from database
            result = await self.db.execute(
                select(Company).where(Company.ticker == ticker.upper())
            )
            company = result.scalar_one_or_none()

            if not company:
                return {"error": f"Company {ticker} not found"}

            # Fetch earnings data from Yahoo Finance
            earnings_data = await self._fetch_yahoo_earnings(ticker)

            # Get upcoming earnings
            upcoming = await self._get_upcoming_earnings(ticker)

            return {
                "ticker": ticker,
                "company_name": company.name,
                "earnings_history": earnings_data.get("history", []),
                "upcoming_earnings": upcoming,
                "next_earnings_date": upcoming[0]["date"] if upcoming else None,
                "earnings_surprises": earnings_data.get("surprises", []),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching earnings for {ticker}: {e}", exc_info=True)
            return {"error": str(e)}

    async def get_earnings_calendar(
        self, days_ahead: int = 30, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get earnings calendar for all companies.

        Args:
            days_ahead: Number of days to look ahead
            limit: Maximum number of companies to return

        Returns:
            List of companies with upcoming earnings
        """
        try:
            # Get all companies from database (don't limit here, we'll limit after filtering)
            result = await self.db.execute(select(Company))
            companies = result.scalars().all()

            if not companies:
                logger.warning("No companies found in database")
                return []

            logger.info(f"Fetching earnings for {len(companies)} companies")

            # Fetch earnings dates for all companies in parallel
            earnings_list = []

            # Process in batches to avoid rate limiting
            batch_size = 10
            for i in range(0, len(companies), batch_size):
                batch = companies[i : i + batch_size]

                tasks = [
                    self._get_upcoming_earnings(company.ticker) for company in batch
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for company, earnings in zip(batch, results):
                    if isinstance(earnings, Exception):
                        logger.debug(
                            f"Error fetching earnings for {company.ticker}: {earnings}"
                        )
                        continue

                    if earnings:
                        for earning in earnings:
                            earnings_list.append(
                                {
                                    "ticker": company.ticker,
                                    "company_name": company.name,
                                    **earning,
                                }
                            )

                # Rate limiting
                await asyncio.sleep(1.0)

            # Filter to upcoming dates only (today or future, within days_ahead)
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)

            upcoming = []
            for e in earnings_list:
                if not e.get("date"):
                    continue
                try:
                    # Parse date string
                    if isinstance(e["date"], str):
                        earning_date = datetime.fromisoformat(
                            e["date"].split("T")[0]
                        ).date()
                    else:
                        earning_date = (
                            e["date"]
                            if hasattr(e["date"], "date")
                            else datetime.fromisoformat(str(e["date"])).date()
                        )

                    # Only include dates from today onwards, within the specified range
                    if today <= earning_date <= end_date:
                        e["date"] = earning_date.isoformat()
                        upcoming.append(e)
                except (ValueError, AttributeError) as ex:
                    logger.debug(
                        f"Error parsing earnings date for {e.get('ticker', 'unknown')}: {ex}"
                    )
                    continue

            # Sort by date (earliest first)
            upcoming.sort(key=lambda x: x.get("date", ""))

            logger.info(
                f"Found {len(upcoming)} companies with earnings in next {days_ahead} days"
            )
            return upcoming[:limit]

        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {e}", exc_info=True)
            return []

    async def _fetch_yahoo_earnings(self, ticker: str) -> Dict[str, Any]:
        """Fetch earnings data from Yahoo Finance."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(self.executor, lambda: yf.Ticker(ticker))

            # Get earnings data
            info = await loop.run_in_executor(self.executor, lambda: stock.info)

            earnings_data = {"history": [], "surprises": []}

            # Extract earnings dates
            if "earningsDate" in info:
                earnings_dates = info.get("earningsDate", [])
                if isinstance(earnings_dates, list) and len(earnings_dates) > 0:
                    if isinstance(earnings_dates[0], (int, float)):
                        # Unix timestamp
                        date = datetime.fromtimestamp(earnings_dates[0])
                        earnings_data["next_earnings_date"] = date.date().isoformat()

            # Get earnings history
            try:
                earnings = await loop.run_in_executor(
                    self.executor, lambda: stock.earnings_history
                )

                if earnings is not None and not earnings.empty:
                    for _, row in earnings.iterrows():
                        earnings_data["history"].append(
                            {
                                "date": row.get("Earnings Date", ""),
                                "estimate": float(row.get("EPS Estimate", 0))
                                if row.get("EPS Estimate")
                                else None,
                                "actual": float(row.get("EPS Actual", 0))
                                if row.get("EPS Actual")
                                else None,
                                "surprise": float(row.get("EPS Surprise(%)", 0))
                                if row.get("EPS Surprise(%)")
                                else None,
                            }
                        )
            except Exception as e:
                logger.debug(f"Could not fetch earnings history: {e}")

            # Get earnings surprises
            try:
                surprises = await loop.run_in_executor(
                    self.executor, lambda: stock.earnings_dates
                )

                if surprises is not None and not surprises.empty:
                    for _, row in surprises.iterrows():
                        earnings_data["surprises"].append(
                            {
                                "date": row.name.strftime("%Y-%m-%d")
                                if hasattr(row.name, "strftime")
                                else str(row.name),
                                "estimate": float(row.get("EPS Estimate", 0))
                                if row.get("EPS Estimate")
                                else None,
                                "actual": float(row.get("EPS Actual", 0))
                                if row.get("EPS Actual")
                                else None,
                            }
                        )
            except Exception as e:
                logger.debug(f"Could not fetch earnings surprises: {e}")

            return earnings_data

        except Exception as e:
            logger.error(f"Error fetching Yahoo earnings for {ticker}: {e}")
            return {"history": [], "surprises": []}

    async def _get_upcoming_earnings(self, ticker: str) -> List[Dict[str, Any]]:
        """Get upcoming earnings dates for a ticker."""
        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(self.executor, lambda: yf.Ticker(ticker))

            info = await loop.run_in_executor(self.executor, lambda: stock.info)

            upcoming = []

            # Check for earnings date - try multiple fields
            today = datetime.now().date()

            # Method 1: earningsDate field
            if "earningsDate" in info:
                earnings_dates = info.get("earningsDate", [])
                if isinstance(earnings_dates, list) and len(earnings_dates) > 0:
                    for date_val in earnings_dates:
                        if isinstance(date_val, (int, float)):
                            try:
                                date = datetime.fromtimestamp(date_val)
                                earning_date = date.date()
                                if earning_date >= today:
                                    upcoming.append(
                                        {
                                            "date": earning_date.isoformat(),
                                            "type": "Quarterly Earnings",
                                            "estimate": info.get(
                                                "earningsQuarterlyGrowth"
                                            ),
                                            "days_until": (earning_date - today).days,
                                        }
                                    )
                            except (ValueError, OSError) as e:
                                logger.debug(
                                    f"Error parsing earnings date timestamp {date_val}: {e}"
                                )

            # Method 2: nextFiscalYearEnd and nextFiscalQuarterEnd
            if not upcoming:
                if "nextFiscalYearEnd" in info and "nextFiscalQuarterEnd" in info:
                    try:
                        year_end = info.get("nextFiscalYearEnd")
                        quarter_end = info.get("nextFiscalQuarterEnd")
                        if year_end and quarter_end:
                            # Estimate earnings date (usually 2-4 weeks after quarter end)
                            quarter_date = datetime.fromtimestamp(quarter_end).date()
                            estimated_earnings = quarter_date + timedelta(
                                days=21
                            )  # ~3 weeks after
                            if estimated_earnings >= today:
                                upcoming.append(
                                    {
                                        "date": estimated_earnings.isoformat(),
                                        "type": "Estimated Quarterly Earnings",
                                        "estimate": info.get("earningsQuarterlyGrowth"),
                                        "days_until": (estimated_earnings - today).days,
                                    }
                                )
                    except (ValueError, TypeError, OSError) as e:
                        logger.debug(f"Error parsing fiscal dates: {e}")

            return upcoming

        except Exception as e:
            logger.debug(f"Error getting upcoming earnings for {ticker}: {e}")
            return []
