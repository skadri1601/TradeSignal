"""
Portfolio Analysis Service.

Handles:
- Virtual portfolio creation and management
- Position sizing calculations
- Risk assessment
- Performance attribution
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.portfolio import (
    VirtualPortfolio,
    PortfolioPosition,
    PortfolioTransaction,
    PortfolioPerformance,
)
from app.models.company import Company

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio analysis and management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_portfolio(
        self, user_id: int, name: str, description: Optional[str] = None
    ) -> VirtualPortfolio:
        """Create a new virtual portfolio."""
        portfolio = VirtualPortfolio(
            user_id=user_id,
            name=name,
            description=description,
        )
        self.db.add(portfolio)
        await self.db.commit()
        await self.db.refresh(portfolio)

        return portfolio

    async def add_position(
        self,
        portfolio_id: int,
        ticker: str,
        shares: float,
        price: float,
        transaction_date: Optional[datetime] = None,
    ) -> PortfolioPosition:
        """Add or update a position in the portfolio."""
        portfolio = await self.db.get(VirtualPortfolio, portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Get or create position
        result = await self.db.execute(
            select(PortfolioPosition).where(
                PortfolioPosition.portfolio_id == portfolio_id,
                PortfolioPosition.ticker == ticker.upper(),
            )
        )
        position = result.scalar_one_or_none()

        if position:
            # Update existing position (average cost calculation)
            total_shares = position.shares + shares
            total_cost = (position.cost_basis + (shares * price))
            new_average_cost = total_cost / total_shares if total_shares > 0 else price

            position.shares = total_shares
            position.average_cost = new_average_cost
            position.cost_basis = total_cost
        else:
            # Create new position
            position = PortfolioPosition(
                portfolio_id=portfolio_id,
                ticker=ticker.upper(),
                shares=shares,
                average_cost=price,
                current_price=price,
                cost_basis=shares * price,
                current_value=shares * price,
                unrealized_gain_loss=0.0,
                unrealized_gain_loss_pct=0.0,
                position_size_pct=0.0,  # Will be calculated
            )
            self.db.add(position)

        # Create transaction record
        transaction = PortfolioTransaction(
            portfolio_id=portfolio_id,
            position_id=position.id if position.id else None,
            ticker=ticker.upper(),
            transaction_type="BUY",
            shares=shares,
            price=price,
            total_value=shares * price,
            transaction_date=transaction_date or datetime.utcnow(),
        )
        self.db.add(transaction)

        # Recalculate portfolio
        await self._recalculate_portfolio(portfolio_id)

        await self.db.commit()
        await self.db.refresh(position)

        return position

    async def remove_position(
        self, portfolio_id: int, ticker: str, shares: float, price: float
    ) -> PortfolioTransaction:
        """Remove shares from a position (sell)."""
        result = await self.db.execute(
            select(PortfolioPosition).where(
                PortfolioPosition.portfolio_id == portfolio_id,
                PortfolioPosition.ticker == ticker.upper(),
            )
        )
        position = result.scalar_one_or_none()

        if not position:
            raise ValueError("Position not found")

        if position.shares < shares:
            raise ValueError("Insufficient shares to sell")

        # Update position
        position.shares -= shares
        if position.shares == 0:
            # Remove position if fully sold
            await self.db.delete(position)
            position_id = None
        else:
            # Recalculate cost basis (FIFO or average cost method)
            # Using average cost method - cost basis reduces proportionally
            position.cost_basis = position.shares * position.average_cost
            position_id = position.id

        # Create sell transaction
        transaction = PortfolioTransaction(
            portfolio_id=portfolio_id,
            position_id=position_id,
            ticker=ticker.upper(),
            transaction_type="SELL",
            shares=shares,
            price=price,
            total_value=shares * price,
            transaction_date=datetime.utcnow(),
        )
        self.db.add(transaction)

        # Recalculate portfolio
        await self._recalculate_portfolio(portfolio_id)

        await self.db.commit()
        await self.db.refresh(transaction)

        return transaction

    async def _recalculate_portfolio(self, portfolio_id: int) -> None:
        """Recalculate portfolio metrics."""
        portfolio = await self.db.get(VirtualPortfolio, portfolio_id)
        if not portfolio:
            return

        # Get all positions
        result = await self.db.execute(
            select(PortfolioPosition).where(
                PortfolioPosition.portfolio_id == portfolio_id
            )
        )
        positions = result.scalars().all()

        # Update position prices and metrics
        total_value = 0.0
        total_cost = 0.0

        for position in positions:
            # Get current price (would fetch from stock service in production)
            # For now, use stored current_price
            current_price = position.current_price

            # Update position metrics
            position.current_price = current_price
            position.current_value = position.shares * current_price
            position.cost_basis = position.shares * position.average_cost
            position.unrealized_gain_loss = (
                position.current_value - position.cost_basis
            )
            position.unrealized_gain_loss_pct = (
                (position.unrealized_gain_loss / position.cost_basis * 100)
                if position.cost_basis > 0
                else 0.0
            )

            total_value += position.current_value
            total_cost += position.cost_basis

        # Calculate position sizes
        for position in positions:
            position.position_size_pct = (
                (position.current_value / total_value * 100) if total_value > 0 else 0.0
            )

        # Update portfolio metrics
        portfolio.total_value = total_value
        portfolio.total_cost = total_cost
        portfolio.total_return = total_value - total_cost
        portfolio.total_return_pct = (
            (portfolio.total_return / total_cost * 100) if total_cost > 0 else 0.0
        )
        portfolio.last_calculated_at = datetime.utcnow()

        # Calculate risk metrics
        portfolio.portfolio_risk_score = await self._calculate_portfolio_risk(positions)
        portfolio.diversification_score = await self._calculate_diversification(positions)

    async def _calculate_portfolio_risk(
        self, positions: List[PortfolioPosition]
    ) -> Optional[float]:
        """Calculate portfolio risk score (0-100, higher = more risky)."""
        if not positions:
            return None

        # Weighted average of position risk scores
        # Would integrate with risk_level_service in production
        total_weighted_risk = 0.0
        total_weight = 0.0

        for position in positions:
            # Default risk score if not available
            risk_score = position.position_risk_score or 50.0
            weight = position.position_size_pct / 100.0

            total_weighted_risk += risk_score * weight
            total_weight += weight

        return total_weighted_risk / total_weight if total_weight > 0 else None

    async def _calculate_diversification(
        self, positions: List[PortfolioPosition]
    ) -> Optional[float]:
        """Calculate diversification score (0-100, higher = more diversified)."""
        if not positions:
            return None

        # Herfindahl-Hirschman Index (HHI) for concentration
        # Lower HHI = more diversified
        hhi = sum((p.position_size_pct / 100.0) ** 2 for p in positions)

        # Convert to diversification score (0-100)
        # HHI ranges from 1/N (perfect diversification) to 1 (perfect concentration)
        # Score = (1 - HHI) * 100, normalized
        max_hhi = 1.0
        min_hhi = 1.0 / len(positions) if len(positions) > 0 else 1.0

        if max_hhi == min_hhi:
            return 50.0  # Default

        normalized_hhi = (hhi - min_hhi) / (max_hhi - min_hhi)
        diversification_score = (1.0 - normalized_hhi) * 100.0

        return max(0.0, min(100.0, diversification_score))

    async def get_portfolio_performance(
        self, portfolio_id: int, days_back: int = 30
    ) -> List[PortfolioPerformance]:
        """Get historical performance snapshots."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        result = await self.db.execute(
            select(PortfolioPerformance)
            .where(
                PortfolioPerformance.portfolio_id == portfolio_id,
                PortfolioPerformance.snapshot_date >= cutoff_date,
            )
            .order_by(desc(PortfolioPerformance.snapshot_date))
        )

        return list(result.scalars().all())

    async def create_performance_snapshot(self, portfolio_id: int) -> PortfolioPerformance:
        """Create a performance snapshot for attribution analysis."""
        portfolio = await self.db.get(VirtualPortfolio, portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Recalculate first
        await self._recalculate_portfolio(portfolio_id)
        await self.db.refresh(portfolio)

        # Create snapshot
        snapshot = PortfolioPerformance(
            portfolio_id=portfolio_id,
            snapshot_date=datetime.utcnow(),
            total_value=portfolio.total_value,
            total_cost=portfolio.total_cost,
            total_return=portfolio.total_return,
            total_return_pct=portfolio.total_return_pct,
            portfolio_risk_score=portfolio.portfolio_risk_score,
        )

        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)

        return snapshot

