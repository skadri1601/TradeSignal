"""
M&A Tracking Service for fetching and analyzing M&A transaction history.

Fetches M&A data from Financial Modeling Prep API and calculates
M&A track record scores for management excellence scoring.
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.models.ma_transaction import MATransaction
from app.models.company import Company

logger = logging.getLogger(__name__)


class MATrackingService:
    """Service for tracking and analyzing M&A transactions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.fmp_api_key = getattr(settings, "financial_modeling_prep_api_key", None)
        self.base_url = "https://financialmodelingprep.com/api/v3"

    async def fetch_ma_transactions(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Fetch M&A transactions from Financial Modeling Prep API.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of M&A transaction dictionaries
        """
        if not self.fmp_api_key:
            logger.warning("Financial Modeling Prep API key not configured")
            return []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/mergers-acquisitions/{ticker}?apikey={self.fmp_api_key}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
                else:
                    logger.warning(f"M&A API returned status {response.status_code} for {ticker}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching M&A transactions for {ticker}: {e}")
            return []

    async def sync_ma_transactions(self, ticker: str) -> int:
        """
        Sync M&A transactions from API to database.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Number of transactions synced
        """
        # Get company
        result = await self.db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        company = result.scalar_one_or_none()
        
        if not company:
            logger.warning(f"Company {ticker} not found")
            return 0

        # Fetch from API
        transactions_data = await self.fetch_ma_transactions(ticker)
        
        if not transactions_data:
            logger.info(f"No M&A transactions found for {ticker}")
            return 0

        synced_count = 0
        for tx_data in transactions_data:
            try:
                # Check if transaction already exists
                deal_date_str = tx_data.get("date", tx_data.get("dealDate", ""))
                if not deal_date_str:
                    continue
                
                try:
                    deal_date = datetime.strptime(deal_date_str.split("T")[0], "%Y-%m-%d").date()
                except (ValueError, AttributeError):
                    continue

                target_company = tx_data.get("targetCompany", tx_data.get("target", "Unknown"))
                deal_value = tx_data.get("dealValue", tx_data.get("value"))
                
                # Check if already exists
                existing = await self.db.execute(
                    select(MATransaction).where(
                        MATransaction.ticker == ticker.upper(),
                        MATransaction.target_company == target_company,
                        MATransaction.deal_date == deal_date,
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Create new transaction
                ma_transaction = MATransaction(
                    company_id=company.id,
                    ticker=ticker.upper(),
                    deal_type=tx_data.get("type", "acquisition").lower(),
                    target_company=target_company,
                    deal_value=float(deal_value) if deal_value else None,
                    deal_date=deal_date,
                    status=tx_data.get("status", "completed").lower(),
                    source="financial_modeling_prep",
                )
                self.db.add(ma_transaction)
                synced_count += 1
            except Exception as e:
                logger.error(f"Error syncing M&A transaction for {ticker}: {e}")
                continue

        if synced_count > 0:
            await self.db.commit()
            logger.info(f"Synced {synced_count} M&A transactions for {ticker}")

        return synced_count

    async def calculate_ma_track_record_score(self, ticker: str) -> float:
        """
        Calculate M&A track record score (0-100) based on historical transactions.

        Factors considered:
        - Deal success rate (completed vs terminated)
        - Deal frequency and timing
        - Deal size relative to company size
        - ROI (if available)
        - Integration success (if available)

        Args:
            ticker: Stock ticker symbol

        Returns:
            M&A track record score (0-100)
        """
        # Get all M&A transactions for the company
        result = await self.db.execute(
            select(MATransaction)
            .where(MATransaction.ticker == ticker.upper())
            .order_by(MATransaction.deal_date.desc())
        )
        transactions = result.scalars().all()

        if not transactions:
            # No hardcoded default - return None to indicate no data
            # The caller should handle this appropriately
            logger.warning(f"No M&A transactions found for {ticker}")
            return None  # Indicates no M&A history available

        # Get company for size comparison
        company_result = await self.db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        company = company_result.scalar_one_or_none()
        company_market_cap = company.market_cap if company and company.market_cap else None

        # Calculate metrics
        total_deals = len(transactions)
        completed_deals = sum(1 for tx in transactions if tx.status == "completed")
        terminated_deals = sum(1 for tx in transactions if tx.status == "terminated")
        
        # Success rate (completed deals / total deals)
        success_rate = (completed_deals / total_deals) if total_deals > 0 else 0.0
        
        # Average deal size (relative to market cap if available)
        deal_values = [tx.deal_value for tx in transactions if tx.deal_value]
        avg_deal_size = sum(deal_values) / len(deal_values) if deal_values else 0
        
        # Deal size appropriateness (deals should be reasonable relative to company size)
        size_score = 1.0
        if company_market_cap and avg_deal_size > 0:
            deal_ratio = avg_deal_size / company_market_cap
            # Ideal: 5-20% of market cap per deal
            if 0.05 <= deal_ratio <= 0.20:
                size_score = 1.0
            elif deal_ratio < 0.05:
                size_score = 0.7  # Too small deals
            else:
                size_score = 0.5  # Too large deals (risky)

        # ROI score (if available)
        roi_scores = [tx.roi for tx in transactions if tx.roi is not None]
        avg_roi = sum(roi_scores) / len(roi_scores) if roi_scores else None
        roi_score = 1.0
        if avg_roi is not None:
            if avg_roi > 10:
                roi_score = 1.0
            elif avg_roi > 5:
                roi_score = 0.8
            elif avg_roi > 0:
                roi_score = 0.6
            else:
                roi_score = 0.3  # Negative ROI

        # Integration success (if available)
        integration_scores = [tx.integration_success for tx in transactions if tx.integration_success is not None]
        avg_integration = sum(integration_scores) / len(integration_scores) if integration_scores else None
        integration_score = avg_integration / 100.0 if avg_integration is not None else 0.7  # Default

        # Calculate composite score (0-100)
        # Weight: success_rate (40%), size_score (20%), roi_score (20%), integration_score (20%)
        composite_score = (
            success_rate * 40 +
            size_score * 20 +
            roi_score * 20 +
            integration_score * 20
        )

        return min(100.0, max(0.0, composite_score))

    async def get_ma_transactions(self, ticker: str, limit: int = 10) -> List[MATransaction]:
        """
        Get M&A transactions for a company.

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of transactions to return

        Returns:
            List of MATransaction objects
        """
        result = await self.db.execute(
            select(MATransaction)
            .where(MATransaction.ticker == ticker.upper())
            .order_by(MATransaction.deal_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

