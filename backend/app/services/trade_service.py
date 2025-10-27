"""
Trade service layer.

Business logic for trade operations.
"""

import logging
from typing import Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.models import Trade, Company, Insider
from app.schemas.trade import TradeCreate, TradeUpdate, TradeFilter, TradeStats

logger = logging.getLogger(__name__)


class TradeService:
    """Service for trade-related operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, trade_id: int) -> Optional[Trade]:
        """
        Get trade by ID with related data.

        Args:
            db: Database session
            trade_id: Trade ID

        Returns:
            Trade instance or None
        """
        result = await db.execute(
            select(Trade)
            .options(selectinload(Trade.company))
            .options(selectinload(Trade.insider))
            .where(Trade.id == trade_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[TradeFilter] = None,
        sort_by: str = "transaction_date",
        order: str = "desc"
    ) -> tuple[List[Trade], int]:
        """
        Get all trades with filtering and pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filter parameters
            sort_by: Field to sort by
            order: Sort order (asc or desc)

        Returns:
            Tuple of (trades list, total count)
        """
        # Build base query
        query = select(Trade).options(
            selectinload(Trade.company),
            selectinload(Trade.insider)
        )

        # Apply filters
        if filters:
            query = TradeService._apply_filters(query, filters)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply sorting
        sort_column = getattr(Trade, sort_by, Trade.transaction_date)
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
    def _apply_filters(query, filters: TradeFilter):
        """
        Apply filters to trade query.

        Args:
            query: SQLAlchemy query
            filters: Filter parameters

        Returns:
            Filtered query
        """
        if filters.company_id:
            query = query.where(Trade.company_id == filters.company_id)

        if filters.insider_id:
            query = query.where(Trade.insider_id == filters.insider_id)

        if filters.ticker:
            query = query.join(Company).where(
                func.upper(Company.ticker) == filters.ticker.upper()
            )

        if filters.transaction_type:
            query = query.where(Trade.transaction_type == filters.transaction_type.upper())

        if filters.transaction_date_from:
            query = query.where(Trade.transaction_date >= filters.transaction_date_from)

        if filters.transaction_date_to:
            query = query.where(Trade.transaction_date <= filters.transaction_date_to)

        if filters.min_value is not None:
            query = query.where(Trade.total_value >= filters.min_value)

        if filters.max_value is not None:
            query = query.where(Trade.total_value <= filters.max_value)

        if filters.min_shares is not None:
            query = query.where(Trade.shares >= filters.min_shares)

        if filters.derivative_only:
            query = query.where(Trade.derivative_transaction == True)

        if filters.significant_only:
            query = query.where(Trade.total_value > 100000)

        return query

    @staticmethod
    async def get_recent(
        db: AsyncSession,
        days: int = 7,
        limit: int = 100
    ) -> List[Trade]:
        """
        Get recent trades.

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum number of trades

        Returns:
            List of recent trades
        """
        cutoff_date = date.today() - timedelta(days=days)

        result = await db.execute(
            select(Trade)
            .options(selectinload(Trade.company), selectinload(Trade.insider))
            .where(Trade.transaction_date >= cutoff_date)
            .order_by(desc(Trade.transaction_date))
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, trade_data: TradeCreate) -> Trade:
        """
        Create a new trade.

        Args:
            db: Database session
            trade_data: Trade creation data

        Returns:
            Created Trade instance
        """
        # Calculate total_value if not provided
        trade_dict = trade_data.model_dump()
        if not trade_dict.get("total_value") and trade_dict.get("shares") and trade_dict.get("price_per_share"):
            trade_dict["total_value"] = Decimal(trade_dict["shares"]) * Decimal(trade_dict["price_per_share"])

        trade = Trade(**trade_dict)
        db.add(trade)
        await db.commit()
        await db.refresh(trade)
        logger.info(f"Created trade: ID {trade.id}, {trade.transaction_type} {trade.shares} shares")
        return trade

    @staticmethod
    async def update(
        db: AsyncSession,
        trade: Trade,
        trade_data: TradeUpdate
    ) -> Trade:
        """
        Update an existing trade.

        Args:
            db: Database session
            trade: Existing Trade instance
            trade_data: Update data

        Returns:
            Updated Trade instance
        """
        update_dict = trade_data.model_dump(exclude_unset=True)

        # Recalculate total_value if shares or price changed
        if "shares" in update_dict or "price_per_share" in update_dict:
            shares = update_dict.get("shares", trade.shares)
            price = update_dict.get("price_per_share", trade.price_per_share)
            if shares and price:
                update_dict["total_value"] = Decimal(shares) * Decimal(price)

        for field, value in update_dict.items():
            setattr(trade, field, value)

        await db.commit()
        await db.refresh(trade)
        logger.info(f"Updated trade: ID {trade.id}")
        return trade

    @staticmethod
    async def delete(db: AsyncSession, trade: Trade) -> None:
        """
        Delete a trade.

        Args:
            db: Database session
            trade: Trade instance to delete
        """
        await db.delete(trade)
        await db.commit()
        logger.info(f"Deleted trade: ID {trade.id}")

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        filters: Optional[TradeFilter] = None
    ) -> TradeStats:
        """
        Calculate trade statistics.

        Args:
            db: Database session
            filters: Optional filters

        Returns:
            TradeStats instance
        """
        # Build base query
        query = select(Trade)
        if filters:
            query = TradeService._apply_filters(query, filters)

        # Total trades
        total_trades_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total_trades = total_trades_result.scalar_one()

        # Total buys
        buy_query = query.where(Trade.transaction_type == "BUY")
        total_buys_result = await db.execute(
            select(func.count()).select_from(buy_query.subquery())
        )
        total_buys = total_buys_result.scalar_one()

        # Total sells
        sell_query = query.where(Trade.transaction_type == "SELL")
        total_sells_result = await db.execute(
            select(func.count()).select_from(sell_query.subquery())
        )
        total_sells = total_sells_result.scalar_one()

        # Sum of shares and value
        sums_result = await db.execute(
            select(
                func.sum(Trade.shares),
                func.sum(Trade.total_value),
                func.avg(Trade.total_value),
                func.max(Trade.total_value)
            ).select_from(query.subquery())
        )
        sums = sums_result.one()

        total_shares_traded = float(sums[0]) if sums[0] else 0.0
        total_value = float(sums[1]) if sums[1] else 0.0
        average_trade_size = float(sums[2]) if sums[2] else 0.0
        largest_trade = float(sums[3]) if sums[3] else None

        # Most active company
        most_active_company_result = await db.execute(
            select(Company.ticker, func.count(Trade.id).label("trade_count"))
            .select_from(query.subquery())
            .join(Company, Company.id == Trade.company_id)
            .group_by(Company.ticker)
            .order_by(desc("trade_count"))
            .limit(1)
        )
        most_active_company_row = most_active_company_result.first()
        most_active_company = most_active_company_row[0] if most_active_company_row else None

        # Most active insider
        most_active_insider_result = await db.execute(
            select(Insider.name, func.count(Trade.id).label("trade_count"))
            .select_from(query.subquery())
            .join(Insider, Insider.id == Trade.insider_id)
            .group_by(Insider.name)
            .order_by(desc("trade_count"))
            .limit(1)
        )
        most_active_insider_row = most_active_insider_result.first()
        most_active_insider = most_active_insider_row[0] if most_active_insider_row else None

        return TradeStats(
            total_trades=total_trades,
            total_buys=total_buys,
            total_sells=total_sells,
            total_shares_traded=total_shares_traded,
            total_value=total_value,
            average_trade_size=average_trade_size,
            largest_trade=largest_trade,
            most_active_company=most_active_company,
            most_active_insider=most_active_insider
        )

    @staticmethod
    async def check_duplicate(
        db: AsyncSession,
        insider_id: int,
        transaction_date: date,
        shares: Decimal,
        price_per_share: Optional[Decimal]
    ) -> bool:
        """
        Check if a trade already exists (to avoid duplicates).

        Args:
            db: Database session
            insider_id: Insider ID
            transaction_date: Transaction date
            shares: Number of shares
            price_per_share: Price per share

        Returns:
            True if duplicate exists, False otherwise
        """
        query = select(Trade).where(
            and_(
                Trade.insider_id == insider_id,
                Trade.transaction_date == transaction_date,
                Trade.shares == shares
            )
        )

        if price_per_share is not None:
            query = query.where(Trade.price_per_share == price_per_share)

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
