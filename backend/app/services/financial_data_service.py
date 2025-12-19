"""
Financial Data Service for fetching real financial data from APIs.

Integrates with Financial Modeling Prep API to fetch:
- Income statements
- Balance sheets
- Cash flow statements
- Key financial metrics
- Industry comparisons
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Service for fetching financial data from external APIs."""

    def __init__(self):
        self.fmp_api_key = getattr(settings, "financial_modeling_prep_api_key", None)
        self.base_url = "https://financialmodelingprep.com/api/v3"

    async def fetch_company_financials(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive financial data for a company.

        Args:
            ticker: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch

        Returns:
            Dictionary with income statement, balance sheet, and cash flow data
        """
        if not self.fmp_api_key:
            logger.warning("Financial Modeling Prep API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch income statement
                income_url = (
                    f"{self.base_url}/income-statement/{ticker}"
                    f"?period={period}&limit={limit}&apikey={self.fmp_api_key}"
                )
                income_response = await client.get(income_url)
                income_data = (
                    income_response.json()
                    if income_response.status_code == 200
                    else []
                )

                # Fetch balance sheet
                balance_url = (
                    f"{self.base_url}/balance-sheet-statement/{ticker}"
                    f"?period={period}&limit={limit}&apikey={self.fmp_api_key}"
                )
                balance_response = await client.get(balance_url)
                balance_data = (
                    balance_response.json()
                    if balance_response.status_code == 200
                    else []
                )

                # Fetch cash flow statement
                cashflow_url = (
                    f"{self.base_url}/cash-flow-statement/{ticker}"
                    f"?period={period}&limit={limit}&apikey={self.fmp_api_key}"
                )
                cashflow_response = await client.get(cashflow_url)
                cashflow_data = (
                    cashflow_response.json()
                    if cashflow_response.status_code == 200
                    else []
                )

                if not income_data:
                    logger.warning(f"No financial data found for {ticker}")
                    return None

                # Extract latest year data
                latest_income = income_data[0] if income_data else {}
                latest_balance = balance_data[0] if balance_data else {}
                latest_cashflow = cashflow_data[0] if cashflow_data else {}

                # Calculate key metrics
                revenue = latest_income.get("revenue", 0)
                gross_profit = latest_income.get("grossProfit", 0)
                operating_income = latest_income.get("operatingIncome", 0)
                net_income = latest_income.get("netIncome", 0)
                total_assets = latest_balance.get("totalAssets", 0)
                total_debt = latest_balance.get("totalDebt", 0)
                total_equity = latest_balance.get("totalStockholdersEquity", 0)
                capex = abs(latest_cashflow.get("capitalExpenditure", 0))

                # Calculate ratios
                gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
                operating_margin = (operating_income / revenue * 100) if revenue > 0 else 0
                net_margin = (net_income / revenue * 100) if revenue > 0 else 0
                debt_to_equity = (total_debt / total_equity) if total_equity > 0 else 0
                capex_as_pct_revenue = (capex / revenue * 100) if revenue > 0 else 0
                roe = (net_income / total_equity * 100) if total_equity > 0 else 0
                roa = (net_income / total_assets * 100) if total_assets > 0 else 0

                # Calculate growth rates (if we have historical data)
                revenue_growth = 0.0
                if len(income_data) >= 2:
                    prev_revenue = income_data[1].get("revenue", 0)
                    if prev_revenue > 0:
                        revenue_growth = ((revenue - prev_revenue) / prev_revenue) * 100

                return {
                    "ticker": ticker,
                    "revenue": revenue,
                    "gross_profit": gross_profit,
                    "operating_income": operating_income,
                    "net_income": net_income,
                    "total_assets": total_assets,
                    "total_debt": total_debt,
                    "total_equity": total_equity,
                    "capex": capex,
                    "gross_margin": gross_margin / 100,  # Convert to decimal
                    "operating_margin": operating_margin / 100,
                    "net_margin": net_margin / 100,
                    "debt_to_equity": debt_to_equity,
                    "capex_as_pct_revenue": capex_as_pct_revenue / 100,
                    "roe": roe / 100,
                    "roa": roa / 100,
                    "revenue_growth": revenue_growth / 100,
                    "shares_outstanding": latest_income.get("weightedAverageShsOut", 0),
                    "fiscal_year": latest_income.get("calendarYear"),
                    "historical_data": {
                        "income_statements": income_data[:3],  # Last 3 years
                        "balance_sheets": balance_data[:3],
                        "cash_flows": cashflow_data[:3],
                    },
                }

        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}", exc_info=True)
            return None

    async def fetch_key_metrics(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch key financial metrics for a company.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with key metrics
        """
        if not self.fmp_api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/key-metrics/{ticker}?limit=1&apikey={self.fmp_api_key}"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data[0] if data else None
        except Exception as e:
            logger.error(f"Error fetching key metrics for {ticker}: {e}")
            return None

    async def calculate_competitive_strength_components(
        self, ticker: str
    ) -> Dict[str, float]:
        """
        Calculate competitive strength component scores from real financial data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with component scores (0-2 each)
        """
        financials = await self.fetch_company_financials(ticker)
        if not financials:
            # No hardcoded defaults - raise error if data unavailable
            logger.error(f"Financial data unavailable for {ticker}. Cannot calculate competitive strength components.")
            raise ValueError(
                f"Financial data not available for {ticker}. "
                "Please ensure Financial Modeling Prep API key is configured and the ticker is valid."
            )

        # Network Effects (0-2): Based on user growth, platform engagement
        # Simplified: Use revenue growth as proxy
        revenue_growth = financials.get("revenue_growth", 0)
        network_effects = min(2.0, max(0.0, (revenue_growth * 10 + 1.0)))  # Scale growth to 0-2

        # Intangible Assets (0-2): R&D spending, brand value
        # Use R&D as % of revenue (if available) or use gross margin as proxy
        gross_margin = financials.get("gross_margin", 0)
        intangible_assets = min(2.0, max(0.0, gross_margin * 2))  # Scale margin to 0-2

        # Cost Advantages (0-2): Gross margins, operating leverage
        operating_margin = financials.get("operating_margin", 0)
        cost_advantages = min(2.0, max(0.0, operating_margin * 2))  # Scale margin to 0-2

        # Switching Costs (0-2): Customer concentration, contract terms
        # Simplified: Use debt-to-equity as proxy (lower = more stable = higher switching costs)
        debt_to_equity = financials.get("debt_to_equity", 0)
        switching_costs = min(2.0, max(0.0, 2.0 - (debt_to_equity * 0.5)))  # Inverse relationship

        # Efficient Scale (0-2): Market share, production capacity
        # Use ROE and ROA as proxies for operational efficiency
        roe = financials.get("roe", 0)
        roa = financials.get("roa", 0)
        efficient_scale = min(2.0, max(0.0, (roe + roa) / 2 * 2))  # Scale to 0-2

        return {
            "network_effects": round(network_effects, 2),
            "intangible_assets": round(intangible_assets, 2),
            "cost_advantages": round(cost_advantages, 2),
            "switching_costs": round(switching_costs, 2),
            "efficient_scale": round(efficient_scale, 2),
        }

    async def calculate_management_score_components(
        self, ticker: str, db: Optional[Any] = None
    ) -> Dict[str, float]:
        """
        Calculate management score component scores from real financial data.

        Args:
            ticker: Stock ticker symbol
            db: Optional database session for M&A tracking (if provided)

        Returns:
            Dictionary with component scores (0-100 each)
        """
        financials = await self.fetch_company_financials(ticker)
        if not financials:
            # No hardcoded defaults - raise error if data unavailable
            logger.error(f"Financial data unavailable for {ticker}. Cannot calculate management score components.")
            raise ValueError(
                f"Financial data not available for {ticker}. "
                "Please ensure Financial Modeling Prep API key is configured and the ticker is valid."
            )

        # M&A Track Record (0-100): Calculate using M&A tracking service if DB provided
        m_and_a = None
        if db:
            try:
                from app.services.ma_tracking_service import MATrackingService
                ma_service = MATrackingService(db)
                # Sync M&A transactions first
                await ma_service.sync_ma_transactions(ticker)
                m_and_a = await ma_service.calculate_ma_track_record_score(ticker)
            except Exception as e:
                logger.warning(f"Could not calculate M&A track record for {ticker}: {e}")
                # If M&A data unavailable, we'll use a calculated default based on company metrics
                # But we still have real financial data, so calculate a reasonable estimate
                # Use company size and financial health as proxy
                revenue = financials.get("revenue", 0)
                if revenue > 0:
                    # Larger, healthier companies tend to have better M&A track records
                    roe = financials.get("roe", 0) * 100
                    m_and_a = min(100.0, max(30.0, roe * 0.8))  # Scale ROE to M&A score estimate
                else:
                    m_and_a = None  # Will be handled by caller
        else:
            # No DB provided, cannot calculate M&A score
            m_and_a = None

        # Capital Discipline (0-100): ROIC, capital allocation efficiency
        roe = financials.get("roe", 0) * 100  # Convert to percentage
        roa = financials.get("roa", 0) * 100
        capital_discipline = min(100.0, max(0.0, (roe + roa) / 2))  # Average of ROE and ROA

        # Shareholder Returns (0-100): TSR, dividend consistency
        # Use ROE as proxy for shareholder returns
        shareholder_returns = min(100.0, max(0.0, roe))

        # Leverage Management (0-100): Debt-to-equity trends, interest coverage
        debt_to_equity = financials.get("debt_to_equity", 0)
        # Lower debt-to-equity = better leverage management
        leverage_management = min(100.0, max(0.0, 100.0 - (debt_to_equity * 10)))

        # Governance (0-100): Board composition, executive compensation
        # Simplified: Use net margin as proxy (well-governed companies tend to have better margins)
        net_margin = financials.get("net_margin", 0) * 100
        governance = min(100.0, max(0.0, net_margin * 2))  # Scale margin to 0-100

        return {
            "m_and_a": round(m_and_a, 2),
            "capital_discipline": round(capital_discipline, 2),
            "shareholder_returns": round(shareholder_returns, 2),
            "leverage_management": round(leverage_management, 2),
            "governance": round(governance, 2),
        }

