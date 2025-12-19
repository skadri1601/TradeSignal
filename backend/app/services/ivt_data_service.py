"""
IVT Data Infrastructure Service.

Integrates with:
- Financial Modeling Prep API
- Benzinga Estimates API
- FRED API (already integrated)
- Nightly batch processing pipeline
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.company import Company
from app.services.dcf_service import DCFService
from app.services.stock_price_service import StockPriceService

logger = logging.getLogger(__name__)


class IVTDataService:
    """Service for fetching and processing IVT data from external APIs."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dcf_service = DCFService(db)
        self.fmp_api_key = getattr(settings, "financial_modeling_prep_api_key", None)
        self.benzinga_api_key = getattr(settings, "benzinga_api_key", None)

    async def fetch_company_financials(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company financials from Financial Modeling Prep API.

        Returns revenue, margins, and other financial metrics.
        """
        if not self.fmp_api_key:
            logger.warning("Financial Modeling Prep API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch income statement
                income_url = (
                    f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}"
                    f"?period=annual&limit=5&apikey={self.fmp_api_key}"
                )
                income_response = await client.get(income_url)
                income_data = income_response.json() if income_response.status_code == 200 else []

                # Fetch balance sheet
                balance_url = (
                    f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}"
                    f"?period=annual&limit=5&apikey={self.fmp_api_key}"
                )
                balance_response = await client.get(balance_url)
                balance_data = balance_response.json() if balance_response.status_code == 200 else []

                # Fetch cash flow statement
                cashflow_url = (
                    f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}"
                    f"?period=annual&limit=5&apikey={self.fmp_api_key}"
                )
                cashflow_response = await client.get(cashflow_url)
                cashflow_data = (
                    cashflow_response.json() if cashflow_response.status_code == 200 else []
                )

                if not income_data:
                    return None

                # Extract latest year data
                latest = income_data[0] if income_data else {}

                # Calculate metrics
                revenue = latest.get("revenue", 0)
                gross_profit = latest.get("grossProfit", 0)
                operating_income = latest.get("operatingIncome", 0)
                net_income = latest.get("netIncome", 0)

                gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
                operating_margin = (operating_income / revenue * 100) if revenue > 0 else 0
                net_margin = (net_income / revenue * 100) if revenue > 0 else 0

                # Get balance sheet data
                latest_balance = balance_data[0] if balance_data else {}
                total_debt = latest_balance.get("totalDebt", 0)
                total_equity = latest_balance.get("totalStockholdersEquity", 0)
                debt_to_equity = (
                    (total_debt / total_equity) if total_equity > 0 else 0
                )

                # Get cash flow data
                latest_cashflow = cashflow_data[0] if cashflow_data else {}
                capex = abs(latest_cashflow.get("capitalExpenditure", 0))
                capex_as_pct_revenue = (capex / revenue * 100) if revenue > 0 else 0

                return {
                    "ticker": ticker,
                    "revenue": revenue,
                    "gross_margin": gross_margin / 100,  # Convert to decimal
                    "operating_margin": operating_margin / 100,
                    "net_margin": net_margin / 100,
                    "debt_to_equity": debt_to_equity,
                    "capex_as_pct_revenue": capex_as_pct_revenue / 100,
                    "shares_outstanding": latest.get("weightedAverageShsOut", 0),
                    "fiscal_year": latest.get("calendarYear"),
                }

        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}", exc_info=True)
            return None

    async def fetch_analyst_estimates(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch analyst estimates from Benzinga API.

        Returns revenue growth estimates and other projections.
        """
        if not self.benzinga_api_key:
            logger.warning("Benzinga API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = (
                    f"https://api.benzinga.com/api/v2.0/calendar/earnings"
                    f"?token={self.benzinga_api_key}&tickers={ticker}&date_from={datetime.now().strftime('%Y-%m-%d')}"
                )
                response = await client.get(url)
                data = response.json() if response.status_code == 200 else {}

                # Extract estimates
                earnings = data.get("earnings", [])
                if earnings:
                    latest = earnings[0]
                    return {
                        "ticker": ticker,
                        "eps_estimate": latest.get("eps_est", 0),
                        "revenue_estimate": latest.get("revenue_est", 0),
                        "revenue_growth_estimate": latest.get("revenue_growth_est", 0),
                        "fiscal_year": latest.get("fiscal_year"),
                    }

        except Exception as e:
            logger.error(f"Error fetching estimates for {ticker}: {e}", exc_info=True)
            return None

    async def calculate_ivt_for_company(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Calculate Intrinsic Value Target for a company.

        Fetches data from APIs and runs DCF calculation.
        """
        # Get company
        result = await self.db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        company = result.scalar_one_or_none()

        if not company:
            logger.warning(f"Company {ticker} not found")
            return None

        # Fetch financial data
        financials = await self.fetch_company_financials(ticker)
        if not financials:
            logger.warning(f"Could not fetch financials for {ticker}")
            return None

        # Fetch analyst estimates
        estimates = await self.fetch_analyst_estimates(ticker)

        # Calculate revenue CAGR (use estimates if available, otherwise historical)
        revenue_cagr = 0.10  # Default 10%
        if estimates and estimates.get("revenue_growth_estimate"):
            revenue_cagr = estimates["revenue_growth_estimate"] / 100
        elif financials.get("revenue"):
            # Calculate historical CAGR (simplified)
            revenue_cagr = 0.10  # Would calculate from historical data

        # Get current stock price from StockPriceService
        try:
            quote = StockPriceService.get_stock_quote(ticker)
            current_price = quote["current_price"] if quote else None

            if not current_price:
                logger.warning(f"Could not fetch stock price for {ticker}, skipping IVT calculation")
                return None
        except Exception as e:
            logger.error(f"Error fetching stock price for {ticker}: {e}")
            return None

        # Calculate IVT using DCF
        ivt_result = self.dcf_service.calculate_intrinsic_value(
            ticker=ticker,
            current_revenue=financials["revenue"],
            revenue_cagr=revenue_cagr,
            gross_margin=financials["gross_margin"],
            operating_margin=financials["operating_margin"],
            net_margin=financials["net_margin"],
            capex_as_pct_revenue=financials["capex_as_pct_revenue"],
            shares_outstanding=financials["shares_outstanding"],
            debt_to_equity=financials["debt_to_equity"],
        )

        # Calculate discount/premium
        discount_premium_pct = (
            ((ivt_result["intrinsic_value"] - current_price) / current_price * 100)
            if current_price > 0
            else 0
        )

        return {
            **ivt_result,
            "current_price": current_price,
            "discount_premium_pct": discount_premium_pct,
        }

    async def batch_process_ivt_calculations(
        self, tickers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Batch process IVT calculations for multiple companies.

        Runs nightly to update all IVT values.
        """
        if not tickers:
            # Get all active companies
            result = await self.db.execute(
                select(Company).where(Company.is_active.is_(True))
            )
            companies = result.scalars().all()
            tickers = [c.ticker for c in companies]

        results = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": [],
        }

        for ticker in tickers:
            try:
                results["processed"] += 1
                ivt_result = await self.calculate_ivt_for_company(ticker)

                if ivt_result:
                    # Save to database (would use IntrinsicValueTarget model)
                    results["succeeded"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{ticker}: Could not calculate IVT")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{ticker}: {str(e)}")
                logger.error(f"Error processing IVT for {ticker}: {e}", exc_info=True)

        return results

