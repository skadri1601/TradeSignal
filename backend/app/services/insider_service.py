"""
Insider service layer.

Business logic for insider operations.
"""

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models import Insider
from app.schemas.insider import InsiderCreate, InsiderUpdate

logger = logging.getLogger(__name__)


class InsiderService:
    """Service for insider-related operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, insider_id: int) -> Optional[Insider]:
        """
        Get insider by ID.

        Args:
            db: Database session
            insider_id: Insider ID

        Returns:
            Insider instance or None
        """
        result = await db.execute(
            select(Insider)
            .options(selectinload(Insider.company))
            .where(Insider.id == insider_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name_and_company(
        db: AsyncSession, name: str, company_id: int
    ) -> Optional[Insider]:
        """
        Get insider by name and company.

        Args:
            db: Database session
            name: Insider name
            company_id: Company ID

        Returns:
            Insider instance or None
        """
        result = await db.execute(
            select(Insider).where(
                and_(Insider.name == name, Insider.company_id == company_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        company_id: Optional[int] = None,
    ) -> tuple[List[Insider], int]:
        """
        Get all insiders with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            company_id: Optional company filter

        Returns:
            Tuple of (insiders list, total count)
        """
        # Build query
        query = select(Insider).options(selectinload(Insider.company))

        # Apply filters
        if company_id:
            query = query.where(Insider.company_id == company_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Insider.name)
        result = await db.execute(query)
        insiders = result.scalars().all()

        return list(insiders), total

    @staticmethod
    async def search(
        db: AsyncSession, query: str, skip: int = 0, limit: int = 20
    ) -> tuple[List[Insider], int]:
        """
        Search insiders by name.

        Args:
            db: Database session
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (insiders list, total count)
        """
        # Search by name (case-insensitive)
        search_filter = func.upper(Insider.name).contains(query.upper())

        # Build query
        search_query = (
            select(Insider).options(selectinload(Insider.company)).where(search_filter)
        )

        # Get total count
        count_query = select(func.count()).select_from(search_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        search_query = search_query.offset(skip).limit(limit).order_by(Insider.name)
        result = await db.execute(search_query)
        insiders = result.scalars().all()

        return list(insiders), total

    @staticmethod
    async def create(db: AsyncSession, insider_data: InsiderCreate) -> Insider:
        """
        Create a new insider.

        Args:
            db: Database session
            insider_data: Insider creation data

        Returns:
            Created Insider instance
        """
        insider = Insider(**insider_data.model_dump())
        db.add(insider)
        await db.commit()
        await db.refresh(insider)
        logger.info(f"Created insider: {insider.name} (ID: {insider.id})")
        return insider

    @staticmethod
    async def update(
        db: AsyncSession, insider: Insider, insider_data: InsiderUpdate
    ) -> Insider:
        """
        Update an existing insider.

        Args:
            db: Database session
            insider: Existing Insider instance
            insider_data: Update data

        Returns:
            Updated Insider instance
        """
        update_dict = insider_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(insider, field, value)

        await db.commit()
        await db.refresh(insider)
        logger.info(f"Updated insider: {insider.name} (ID: {insider.id})")
        return insider

    @staticmethod
    async def delete(db: AsyncSession, insider: Insider) -> None:
        """
        Delete an insider.

        Args:
            db: Database session
            insider: Insider instance to delete
        """
        await db.delete(insider)
        await db.commit()
        logger.info(f"Deleted insider: {insider.name} (ID: {insider.id})")

    @staticmethod
    async def get_or_create(
        db: AsyncSession,
        name: str,
        company_id: int,
        title: Optional[str] = None,
        is_director: bool = False,
        is_officer: bool = False,
        is_ten_percent_owner: bool = False,
        is_other: bool = False,
    ) -> Insider:
        """
        Get existing insider or create if doesn't exist.

        Args:
            db: Database session
            name: Insider name
            company_id: Company ID
            title: Optional job title
            is_director: Is board director
            is_officer: Is corporate officer
            is_ten_percent_owner: Owns 10%+ stock
            is_other: Other relationship

        Returns:
            Insider instance
        """
        # Try to find existing insider
        insider = await InsiderService.get_by_name_and_company(db, name, company_id)

        if insider:
            # Update fields if provided
            updated = False
            if title and insider.title != title:
                insider.title = title
                updated = True
            if insider.is_director != is_director:
                insider.is_director = is_director
                updated = True
            if insider.is_officer != is_officer:
                insider.is_officer = is_officer
                updated = True
            if insider.is_ten_percent_owner != is_ten_percent_owner:
                insider.is_ten_percent_owner = is_ten_percent_owner
                updated = True
            if insider.is_other != is_other:
                insider.is_other = is_other
                updated = True

            if updated:
                await db.commit()
                await db.refresh(insider)

            return insider

        # Create new insider
        insider_data = InsiderCreate(
            name=name,
            company_id=company_id,
            title=title,
            is_director=is_director,
            is_officer=is_officer,
            is_ten_percent_owner=is_ten_percent_owner,
            is_other=is_other,
        )
        return await InsiderService.create(db, insider_data)
