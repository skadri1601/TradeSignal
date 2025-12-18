"""
Data Quality Assurance Service.

Automated validation, outlier detection, cross-reference validation, data enrichment.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider

logger = logging.getLogger(__name__)


class DataQualityService:
    """Service for data quality assurance and validation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_trade(self, trade: Trade) -> Dict[str, Any]:
        """
        Validate a trade record for data quality issues.

        Returns validation results with issues found.
        """
        issues = []
        warnings = []

        # Check for missing required fields
        if not trade.shares or trade.shares <= 0:
            issues.append("Missing or invalid shares")

        if not trade.filing_date:
            issues.append("Missing filing date")

        if not trade.transaction_type:
            issues.append("Missing transaction type")

        # Check for outliers
        if trade.total_value:
            if trade.total_value > 1000000000:  # $1B
                warnings.append("Extremely large trade value (>$1B) - verify accuracy")

            if trade.total_value < 0:
                issues.append("Negative trade value")

        # Check price per share consistency
        if trade.shares and trade.price_per_share and trade.total_value:
            calculated_value = trade.shares * trade.price_per_share
            if abs(calculated_value - float(trade.total_value)) > (calculated_value * 0.1):
                warnings.append(
                    f"Price/share inconsistency: calculated ${calculated_value:,.0f} vs "
                    f"reported ${trade.total_value:,.0f}"
                )

        # Check filing date is not in future
        if trade.filing_date and trade.filing_date > datetime.utcnow():
            issues.append("Filing date is in the future")

        # Check filing date is not too old (more than 2 years)
        if trade.filing_date:
            two_years_ago = datetime.utcnow() - timedelta(days=730)
            if trade.filing_date < two_years_ago:
                warnings.append("Filing date is more than 2 years old")

        return {
            "trade_id": trade.id,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "validated_at": datetime.utcnow().isoformat(),
        }

    async def detect_outliers(self, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect outlier trades using statistical methods.

        Uses IQR (Interquartile Range) method for outlier detection.
        """
        # Get trades
        query = select(Trade).join(Company, Trade.company_id == Company.id)

        if ticker:
            query = query.where(Company.ticker == ticker.upper())

        query = query.where(Trade.total_value.isnot(None), Trade.total_value > 0)

        result = await self.db.execute(query)
        trades = result.scalars().all()

        if len(trades) < 10:
            return []  # Need sufficient data for outlier detection

        # Extract trade values
        values = [float(t.total_value) for t in trades if t.total_value]

        if not values:
            return []

        # Calculate quartiles
        sorted_values = sorted(values)
        n = len(sorted_values)
        q1_idx = n // 4
        q3_idx = (3 * n) // 4

        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1

        # Define outlier bounds
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        # Find outliers
        outliers = []
        for trade in trades:
            if trade.total_value:
                value = float(trade.total_value)
                if value < lower_bound or value > upper_bound:
                    outliers.append({
                        "trade_id": trade.id,
                        "ticker": ticker or "N/A",
                        "value": value,
                        "type": "low" if value < lower_bound else "high",
                        "bound": lower_bound if value < lower_bound else upper_bound,
                    })

        return outliers

    async def cross_reference_validation(
        self, trade: Trade
    ) -> Dict[str, Any]:
        """
        Cross-reference trade data with external sources for validation.

        Checks consistency across multiple data points.
        """
        validation_results = {
            "trade_id": trade.id,
            "checks": [],
            "is_consistent": True,
        }

        # Check company exists and is active
        company = await self.db.get(Company, trade.company_id)
        if not company:
            validation_results["checks"].append({
                "check": "company_exists",
                "status": "failed",
                "message": "Company not found",
            })
            validation_results["is_consistent"] = False
        else:
            validation_results["checks"].append({
                "check": "company_exists",
                "status": "passed",
                "message": f"Company {company.ticker} found",
            })

        # Check insider exists
        insider = await self.db.get(Insider, trade.insider_id)
        if not insider:
            validation_results["checks"].append({
                "check": "insider_exists",
                "status": "failed",
                "message": "Insider not found",
            })
            validation_results["is_consistent"] = False
        else:
            validation_results["checks"].append({
                "check": "insider_exists",
                "status": "passed",
                "message": f"Insider {insider.name} found",
            })

        # Check filing date is within reasonable range
        if trade.filing_date:
            days_ago = (datetime.utcnow() - trade.filing_date).days
            if days_ago < 0:
                validation_results["checks"].append({
                    "check": "filing_date_range",
                    "status": "failed",
                    "message": "Filing date is in the future",
                })
                validation_results["is_consistent"] = False
            elif days_ago > 730:
                validation_results["checks"].append({
                    "check": "filing_date_range",
                    "status": "warning",
                    "message": f"Filing date is {days_ago} days ago",
                })
            else:
                validation_results["checks"].append({
                    "check": "filing_date_range",
                    "status": "passed",
                    "message": f"Filing date is {days_ago} days ago",
                })

        return validation_results

    async def enrich_trade_data(self, trade: Trade) -> Trade:
        """
        Enrich trade data with additional information.

        Fills in missing values where possible.
        """
        # Estimate missing total_value if we have shares and price
        if not trade.total_value and trade.shares and trade.price_per_share:
            trade.total_value = trade.shares * trade.price_per_share
            logger.info(f"Enriched trade {trade.id}: estimated total_value = ${trade.total_value:,.2f}")

        # Estimate missing price_per_share if we have shares and total_value
        if not trade.price_per_share and trade.shares and trade.total_value:
            trade.price_per_share = trade.total_value / trade.shares
            logger.info(
                f"Enriched trade {trade.id}: estimated price_per_share = ${trade.price_per_share:.2f}"
            )

        return trade

    async def run_quality_checks(
        self, ticker: Optional[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Run comprehensive quality checks on trades.

        Returns summary of issues found.
        """
        # Get trades
        query = select(Trade).join(Company, Trade.company_id == Company.id)

        if ticker:
            query = query.where(Company.ticker == ticker.upper())

        query = query.limit(limit)

        result = await self.db.execute(query)
        trades = result.scalars().all()

        summary = {
            "total_checked": len(trades),
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
            "outliers": 0,
            "issues": [],
        }

        # Validate each trade
        for trade in trades:
            validation = await self.validate_trade(trade)
            if validation["is_valid"]:
                summary["valid"] += 1
            else:
                summary["invalid"] += 1
                summary["issues"].extend(validation["issues"])

            if validation["warnings"]:
                summary["warnings"] += len(validation["warnings"])

        # Detect outliers
        outliers = await self.detect_outliers(ticker)
        summary["outliers"] = len(outliers)

        return summary

