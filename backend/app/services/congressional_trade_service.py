"""
Congressional Trade service layer.

Business logic for congressional trade operations.
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.models import CongressionalTrade, Congressperson
from app.schemas.congressional_trade import (
    CongressionalTradeFilter,
    CongressionalTradeStats,
)

logger = logging.getLogger(__name__)


class CongressionalTradeService:
    """Service for congressional trade operations."""

    @staticmethod
    async def get_by_id(
        db: AsyncSession, trade_id: int
    ) -> Optional[CongressionalTrade]:
        """Get congressional trade by ID with related data."""
        result = await db.execute(
            select(CongressionalTrade)
            .options(selectinload(CongressionalTrade.company))
            .options(selectinload(CongressionalTrade.congressperson))
            .where(CongressionalTrade.id == trade_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[CongressionalTradeFilter] = None,
        sort_by: str = "transaction_date",
        order: str = "desc",
    ) -> tuple[List[CongressionalTrade], int]:
        """Get all congressional trades with filtering and pagination."""
        # Build base query
        query = select(CongressionalTrade).options(
            selectinload(CongressionalTrade.company),
            selectinload(CongressionalTrade.congressperson),
        )

        # Apply filters
        if filters:
            query = CongressionalTradeService._apply_filters(query, filters)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply sorting
        sort_column = getattr(
            CongressionalTrade, sort_by, CongressionalTrade.transaction_date
        )
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        trades = result.scalars().all()

        return list(trades), total

    @staticmethod
    def _apply_filters(query, filters: CongressionalTradeFilter):
        """Apply filters to congressional trade query."""
        if filters.congressperson_id:
            query = query.where(
                CongressionalTrade.congressperson_id == filters.congressperson_id
            )

        if filters.company_id:
            query = query.where(CongressionalTrade.company_id == filters.company_id)

        if filters.ticker:
            query = query.where(CongressionalTrade.ticker == filters.ticker.upper())

        if filters.transaction_type:
            query = query.where(
                CongressionalTrade.transaction_type == filters.transaction_type.upper()
            )

        if filters.owner_type:
            query = query.where(CongressionalTrade.owner_type == filters.owner_type)

        if filters.transaction_date_from:
            query = query.where(
                CongressionalTrade.transaction_date >= filters.transaction_date_from
            )

        if filters.transaction_date_to:
            query = query.where(
                CongressionalTrade.transaction_date <= filters.transaction_date_to
            )

        if filters.min_value:
            query = query.where(
                CongressionalTrade.amount_estimated >= Decimal(str(filters.min_value))
            )

        if filters.max_value:
            query = query.where(
                CongressionalTrade.amount_estimated <= Decimal(str(filters.max_value))
            )

        if filters.significant_only:
            from app.config import settings

            query = query.where(
                CongressionalTrade.amount_estimated
                > settings.significant_trade_threshold
            )

        # Filter by chamber, state, or party via congressperson join
        if filters.chamber or filters.state or filters.party:
            query = query.join(Congressperson)

            if filters.chamber:
                query = query.where(Congressperson.chamber == filters.chamber.upper())

            if filters.state:
                query = query.where(Congressperson.state == filters.state.upper())

            if filters.party:
                query = query.where(Congressperson.party == filters.party.upper())

        return query

    @staticmethod
    async def get_recent_trades(
        db: AsyncSession, days: int = 7, limit: int = 100
    ) -> List[CongressionalTrade]:
        """Get recent congressional trades."""
        cutoff_date = datetime.now().date() - timedelta(days=days)

        result = await db.execute(
            select(CongressionalTrade)
            .options(selectinload(CongressionalTrade.company))
            .options(selectinload(CongressionalTrade.congressperson))
            .where(CongressionalTrade.transaction_date >= cutoff_date)
            .order_by(desc(CongressionalTrade.transaction_date))
            .limit(limit)
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_trade_stats(
        db: AsyncSession, filters: Optional[CongressionalTradeFilter] = None
    ) -> CongressionalTradeStats:
        """Calculate aggregate statistics for congressional trades."""
        # Build base query with eager loading
        query = select(CongressionalTrade).options(
            selectinload(CongressionalTrade.congressperson)
        )

        # Apply filters
        if filters:
            query = CongressionalTradeService._apply_filters(query, filters)

        # Execute query
        result = await db.execute(query)
        trades = result.scalars().all()

        if not trades:
            return CongressionalTradeStats()

        # Calculate statistics
        total_trades = len(trades)
        buys = [t for t in trades if t.is_buy]
        sells = [t for t in trades if t.is_sell]

        # Calculate values
        buy_values = [float(t.estimated_value) for t in buys if t.estimated_value]
        sell_values = [float(t.estimated_value) for t in sells if t.estimated_value]

        total_buy_value = sum(buy_values) if buy_values else 0.0
        total_sell_value = sum(sell_values) if sell_values else 0.0

        all_values = buy_values + sell_values
        average_trade_size = sum(all_values) / len(all_values) if all_values else 0.0
        largest_trade = max(all_values) if all_values else None

        # Most active congressperson
        most_active = None
        if trades:
            from collections import Counter

            congressperson_counts = Counter([t.congressperson_id for t in trades])
            if congressperson_counts:
                most_active_id = congressperson_counts.most_common(1)[0][0]
                most_active_trade = next(
                    (t for t in trades if t.congressperson_id == most_active_id), None
                )
                if most_active_trade and most_active_trade.congressperson:
                    most_active = most_active_trade.congressperson.name

        # Most active company
        most_active_company = None
        if trades:
            from collections import Counter

            company_counts = Counter([t.ticker for t in trades if t.ticker])
            if company_counts:
                most_active_company = company_counts.most_common(1)[0][0]

        # Chamber breakdown
        house_trades = [
            t
            for t in trades
            if t.congressperson and t.congressperson.chamber == "HOUSE"
        ]
        senate_trades = [
            t
            for t in trades
            if t.congressperson and t.congressperson.chamber == "SENATE"
        ]

        # Party breakdown
        democrat_buys = len(
            [
                t
                for t in buys
                if t.congressperson and t.congressperson.party == "DEMOCRAT"
            ]
        )
        democrat_sells = len(
            [
                t
                for t in sells
                if t.congressperson and t.congressperson.party == "DEMOCRAT"
            ]
        )
        republican_buys = len(
            [
                t
                for t in buys
                if t.congressperson and t.congressperson.party == "REPUBLICAN"
            ]
        )
        republican_sells = len(
            [
                t
                for t in sells
                if t.congressperson and t.congressperson.party == "REPUBLICAN"
            ]
        )

        return CongressionalTradeStats(
            total_trades=total_trades,
            total_buys=len(buys),
            total_sells=len(sells),
            total_value=total_buy_value - total_sell_value,
            total_buy_value=total_buy_value,
            total_sell_value=total_sell_value,
            average_trade_size=average_trade_size,
            largest_trade=largest_trade,
            most_active_congressperson=most_active,
            most_active_company=most_active_company,
            house_trade_count=len(house_trades),
            senate_trade_count=len(senate_trades),
            democrat_buy_count=democrat_buys,
            democrat_sell_count=democrat_sells,
            republican_buy_count=republican_buys,
            republican_sell_count=republican_sells,
        )
