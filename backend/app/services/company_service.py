"""
Company service layer.

Business logic for company operations.
"""

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyWithStats

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for company-related operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, company_id: int) -> Optional[Company]:
        """
        Get company by ID.

        Args:
            db: Database session
            company_id: Company ID

        Returns:
            Company instance or None
        """
        result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_ticker(db: AsyncSession, ticker: str) -> Optional[Company]:
        """
        Get company by ticker symbol.

        Args:
            db: Database session
            ticker: Stock ticker (case-insensitive)

        Returns:
            Company instance or None
        """
        result = await db.execute(
            select(Company).where(func.upper(Company.ticker) == ticker.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_cik(db: AsyncSession, cik: str) -> Optional[Company]:
        """
        Get company by CIK.

        Args:
            db: Database session
            cik: SEC Central Index Key

        Returns:
            Company instance or None
        """
        result = await db.execute(
            select(Company).where(Company.cik == cik)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        sector: Optional[str] = None
    ) -> tuple[List[Company], int]:
        """
        Get all companies with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            sector: Optional sector filter

        Returns:
            Tuple of (companies list, total count)
        """
        # Build query
        query = select(Company)

        # Apply filters
        if sector:
            query = query.where(Company.sector == sector)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Company.ticker)
        result = await db.execute(query)
        companies = result.scalars().all()

        return list(companies), total

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Company], int]:
        """
        Search companies by ticker or name.

        Args:
            db: Database session
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (companies list, total count)
        """
        # Search by ticker or name (case-insensitive)
        search_filter = or_(
            func.upper(Company.ticker).contains(query.upper()),
            func.upper(Company.name).contains(query.upper())
        )

        # Build query
        search_query = select(Company).where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(search_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        search_query = search_query.offset(skip).limit(limit).order_by(Company.ticker)
        result = await db.execute(search_query)
        companies = result.scalars().all()

        return list(companies), total

    @staticmethod
    async def create(db: AsyncSession, company_data: CompanyCreate) -> Company:
        """
        Create a new company.

        Args:
            db: Database session
            company_data: Company creation data

        Returns:
            Created Company instance
        """
        company = Company(**company_data.model_dump())
        db.add(company)
        await db.commit()
        await db.refresh(company)
        logger.info(f"Created company: {company.ticker} (ID: {company.id})")
        return company

    @staticmethod
    async def update(
        db: AsyncSession,
        company: Company,
        company_data: CompanyUpdate
    ) -> Company:
        """
        Update an existing company.

        Args:
            db: Database session
            company: Existing Company instance
            company_data: Update data

        Returns:
            Updated Company instance
        """
        update_dict = company_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(company, field, value)

        await db.commit()
        await db.refresh(company)
        logger.info(f"Updated company: {company.ticker} (ID: {company.id})")
        return company

    @staticmethod
    async def delete(db: AsyncSession, company: Company) -> None:
        """
        Delete a company.

        Args:
            db: Database session
            company: Company instance to delete
        """
        await db.delete(company)
        await db.commit()
        logger.info(f"Deleted company: {company.ticker} (ID: {company.id})")

    @staticmethod
    async def get_or_create(
        db: AsyncSession,
        ticker: str,
        cik: str,
        name: Optional[str] = None
    ) -> Company:
        """
        Get existing company or create if doesn't exist.

        Args:
            db: Database session
            ticker: Stock ticker
            cik: SEC CIK
            name: Optional company name

        Returns:
            Company instance
        """
        # Try to find by CIK first
        company = await CompanyService.get_by_cik(db, cik)

        if company:
            # Update ticker if changed
            if company.ticker != ticker.upper():
                company.ticker = ticker.upper()
                await db.commit()
                await db.refresh(company)
            return company

        # Try to find by ticker
        company = await CompanyService.get_by_ticker(db, ticker)
        if company:
            return company

        # Create new company
        company_data = CompanyCreate(
            ticker=ticker.upper(),
            cik=cik,
            name=name
        )
        return await CompanyService.create(db, company_data)

    @staticmethod
    async def get_with_stats(
        db: AsyncSession,
        company_id: int
    ) -> Optional[CompanyWithStats]:
        """
        Get company with trading statistics.

        Args:
            db: Database session
            company_id: Company ID

        Returns:
            CompanyWithStats instance or None
        """
        from app.models import Trade, Insider

        # Get company
        company = await CompanyService.get_by_id(db, company_id)
        if not company:
            return None

        # Get statistics
        # Total trades
        total_trades_result = await db.execute(
            select(func.count()).where(Trade.company_id == company_id)
        )
        total_trades = total_trades_result.scalar_one()

        # Total insiders
        total_insiders_result = await db.execute(
            select(func.count(func.distinct(Insider.id)))
            .join(Trade, Trade.insider_id == Insider.id)
            .where(Trade.company_id == company_id)
        )
        total_insiders = total_insiders_result.scalar_one()

        # Recent buys/sells (last 30 days)
        from datetime import date, timedelta
        thirty_days_ago = date.today() - timedelta(days=30)

        recent_buys_result = await db.execute(
            select(func.count())
            .where(Trade.company_id == company_id)
            .where(Trade.transaction_date >= thirty_days_ago)
            .where(Trade.transaction_type == "BUY")
        )
        recent_buy_count = recent_buys_result.scalar_one()

        recent_sells_result = await db.execute(
            select(func.count())
            .where(Trade.company_id == company_id)
            .where(Trade.transaction_date >= thirty_days_ago)
            .where(Trade.transaction_type == "SELL")
        )
        recent_sell_count = recent_sells_result.scalar_one()

        # Create response with stats
        return CompanyWithStats(
            **company.to_dict(),
            total_trades=total_trades,
            total_insiders=total_insiders,
            recent_buy_count=recent_buy_count,
            recent_sell_count=recent_sell_count
        )
