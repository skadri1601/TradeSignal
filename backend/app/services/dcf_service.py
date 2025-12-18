"""
DCF (Discounted Cash Flow) Model Service.

Calculates intrinsic value targets using:
- Revenue projection (10-year CAGR, analyst consensus)
- Margin forecasting (gross, operating, net)
- Cash flow calculations (operating CF, capex, FCF)
- WACC calculation (risk-free rate, beta, equity risk premium)
- Terminal value estimation (perpetuity growth method)
- Present value calculation engine
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DCFService:
    """Service for DCF-based intrinsic value calculations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def calculate_intrinsic_value(
        self,
        ticker: str,
        current_revenue: float,
        revenue_cagr: float,  # 10-year CAGR (e.g., 0.10 = 10%)
        gross_margin: float,  # Current gross margin (e.g., 0.40 = 40%)
        operating_margin: float,  # Current operating margin
        net_margin: float,  # Current net margin
        capex_as_pct_revenue: float,  # CapEx as % of revenue
        shares_outstanding: float,
        risk_free_rate: float = 0.04,  # 4% default (10-year Treasury)
        beta: float = 1.0,  # Market beta
        equity_risk_premium: float = 0.06,  # 6% default
        debt_to_equity: float = 0.0,
        cost_of_debt: float = 0.05,  # 5% default
        tax_rate: float = 0.21,  # 21% corporate tax rate
        terminal_growth_rate: float = 0.025,  # 2.5% perpetuity growth
        projection_years: int = 10,
    ) -> Dict[str, Any]:
        """
        Calculate intrinsic value using DCF model.

        Args:
            ticker: Stock ticker symbol
            current_revenue: Current annual revenue
            revenue_cagr: 10-year revenue growth rate (e.g., 0.10 = 10%)
            gross_margin: Current gross margin (e.g., 0.40 = 40%)
            operating_margin: Current operating margin
            net_margin: Current net margin
            capex_as_pct_revenue: CapEx as % of revenue
            shares_outstanding: Number of shares outstanding
            risk_free_rate: Risk-free rate (10-year Treasury)
            beta: Stock beta vs. market
            equity_risk_premium: Equity risk premium
            debt_to_equity: Debt-to-equity ratio
            cost_of_debt: Cost of debt
            tax_rate: Corporate tax rate
            terminal_growth_rate: Terminal growth rate (perpetuity)
            projection_years: Number of years to project (default: 10)

        Returns:
            Dictionary with DCF calculation results
        """
        # Calculate WACC
        wacc = self._calculate_wacc(
            risk_free_rate, beta, equity_risk_premium, debt_to_equity, cost_of_debt, tax_rate
        )

        # Project cash flows
        projected_cash_flows = self._project_cash_flows(
            current_revenue,
            revenue_cagr,
            gross_margin,
            operating_margin,
            net_margin,
            capex_as_pct_revenue,
            tax_rate,
            projection_years,
        )

        # Calculate present value of projected cash flows
        pv_cash_flows = self._calculate_present_value(
            projected_cash_flows["free_cash_flows"], wacc
        )

        # Calculate terminal value
        terminal_value = self._calculate_terminal_value(
            projected_cash_flows["free_cash_flows"][-1],
            terminal_growth_rate,
            wacc,
        )

        # Present value of terminal value
        pv_terminal = terminal_value / ((1 + wacc) ** projection_years)

        # Enterprise value
        enterprise_value = pv_cash_flows + pv_terminal

        # Equity value (assuming no net debt for simplicity)
        equity_value = enterprise_value

        # Intrinsic value per share
        intrinsic_value_per_share = equity_value / shares_outstanding

        return {
            "ticker": ticker,
            "intrinsic_value": round(intrinsic_value_per_share, 2),
            "enterprise_value": round(enterprise_value, 2),
            "equity_value": round(equity_value, 2),
            "wacc": round(wacc, 4),
            "terminal_value": round(terminal_value, 2),
            "pv_cash_flows": round(pv_cash_flows, 2),
            "pv_terminal": round(pv_terminal, 2),
            "assumptions": {
                "revenue_cagr": revenue_cagr,
                "terminal_growth_rate": terminal_growth_rate,
                "risk_free_rate": risk_free_rate,
                "beta": beta,
                "equity_risk_premium": equity_risk_premium,
                "tax_rate": tax_rate,
            },
            "projected_cash_flows": projected_cash_flows,
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def _calculate_wacc(
        self,
        risk_free_rate: float,
        beta: float,
        equity_risk_premium: float,
        debt_to_equity: float,
        cost_of_debt: float,
        tax_rate: float,
    ) -> float:
        """
        Calculate Weighted Average Cost of Capital (WACC).

        WACC = (E/V * Re) + (D/V * Rd * (1 - Tc))
        Where:
        - E = Market value of equity
        - D = Market value of debt
        - V = E + D
        - Re = Cost of equity = Rf + β * (Rm - Rf)
        - Rd = Cost of debt
        - Tc = Tax rate
        """
        # Cost of equity (CAPM)
        cost_of_equity = risk_free_rate + beta * equity_risk_premium

        # If no debt, WACC = cost of equity
        if debt_to_equity == 0:
            return cost_of_equity

        # Calculate weights
        # D/E ratio means: D = debt_to_equity * E
        # V = E + D = E + (debt_to_equity * E) = E * (1 + debt_to_equity)
        # E/V = 1 / (1 + debt_to_equity)
        # D/V = debt_to_equity / (1 + debt_to_equity)
        equity_weight = 1 / (1 + debt_to_equity)
        debt_weight = debt_to_equity / (1 + debt_to_equity)

        # WACC calculation
        wacc = (
            equity_weight * cost_of_equity
            + debt_weight * cost_of_debt * (1 - tax_rate)
        )

        return wacc

    def _project_cash_flows(
        self,
        current_revenue: float,
        revenue_cagr: float,
        gross_margin: float,
        operating_margin: float,
        net_margin: float,
        capex_as_pct_revenue: float,
        tax_rate: float,
        years: int,
    ) -> Dict[str, Any]:
        """
        Project free cash flows for N years.

        Returns:
            Dictionary with revenue, operating_cf, capex, and free_cash_flows arrays
        """
        revenues = []
        operating_cfs = []
        capexs = []
        free_cash_flows = []

        revenue = current_revenue

        for year in range(1, years + 1):
            revenues.append(revenue)

            # Operating cash flow = Revenue * Operating Margin * (1 - Tax Rate)
            # Simplified: Operating CF ≈ Net Income + Depreciation
            # Using net margin as proxy
            operating_cf = revenue * net_margin
            operating_cfs.append(operating_cf)

            # CapEx
            capex = revenue * capex_as_pct_revenue
            capexs.append(capex)

            # Free Cash Flow = Operating CF - CapEx
            fcf = operating_cf - capex
            free_cash_flows.append(fcf)

            # Grow revenue for next year
            revenue = revenue * (1 + revenue_cagr)

        return {
            "revenues": revenues,
            "operating_cash_flows": operating_cfs,
            "capex": capexs,
            "free_cash_flows": free_cash_flows,
        }

    def _calculate_present_value(
        self, cash_flows: List[float], discount_rate: float
    ) -> float:
        """Calculate present value of cash flows."""
        pv = 0.0
        for year, cf in enumerate(cash_flows, start=1):
            pv += cf / ((1 + discount_rate) ** year)
        return pv

    def _calculate_terminal_value(
        self, final_fcf: float, growth_rate: float, discount_rate: float
    ) -> float:
        """
        Calculate terminal value using perpetuity growth method.

        TV = FCF_n+1 / (WACC - g)
        Where FCF_n+1 = FCF_n * (1 + g)
        """
        if discount_rate <= growth_rate:
            # Invalid: discount rate must exceed growth rate
            logger.warning(
                f"Discount rate ({discount_rate}) <= growth rate ({growth_rate}). "
                "Using growth rate = discount_rate - 0.01"
            )
            growth_rate = discount_rate - 0.01

        next_year_fcf = final_fcf * (1 + growth_rate)
        terminal_value = next_year_fcf / (discount_rate - growth_rate)

        return terminal_value

    async def get_latest_ivt(self, ticker: str) -> Optional[Any]:
        """Get the latest IVT for a ticker."""
        from app.models.intrinsic_value import IntrinsicValueTarget
        from sqlalchemy import select

        result = await self.db.execute(
            select(IntrinsicValueTarget)
            .where(IntrinsicValueTarget.ticker == ticker.upper())
            .order_by(IntrinsicValueTarget.calculated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

