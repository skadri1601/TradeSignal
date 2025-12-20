"""
Tier limit enforcement service.

Checks user subscription tier and enforces usage limits.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.subscription import Subscription, TIER_LIMITS, SubscriptionTier
from app.models.usage import UsageTracking


class TierService:
    """Service for managing subscription tiers and enforcing limits."""

    @staticmethod
    async def get_user_tier(user_id: int, db: AsyncSession) -> str:
        """
        Get user's subscription tier.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Tier name (free/basic/pro/enterprise)
        """
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription or not subscription.is_active:
            return SubscriptionTier.FREE.value

        return subscription.tier

    @staticmethod
    async def get_tier_limits(tier: str) -> Dict[str, Any]:
        """
        Get limits for a subscription tier.

        Args:
            tier: Tier name

        Returns:
            Dictionary of limits
        """
        # Map "basic" to "plus" for backward compatibility
        if tier == "basic":
            tier = "plus"

        return TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE.value])

    @staticmethod
    async def get_or_create_usage(user_id: int, db: AsyncSession) -> UsageTracking:
        """
        Get or create today's usage record for user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            UsageTracking instance
        """
        today = date.today()

        result = await db.execute(
            select(UsageTracking).where(
                UsageTracking.user_id == user_id, UsageTracking.date == today
            )
        )
        usage = result.scalar_one_or_none()

        if not usage:
            usage = UsageTracking(user_id=user_id, date=today)
            db.add(usage)
            await db.commit()
            await db.refresh(usage)

        return usage

    @staticmethod
    async def check_ai_limit(user_id: int, db: AsyncSession) -> bool:  # noqa: S3516
        """
        Check if user can make AI request.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if allowed, raises HTTPException if limit exceeded
        """
        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)
        usage = await TierService.get_or_create_usage(user_id, db)

        # Updated key name from subscription.py
        ai_limit = limits.get("ai_requests_limit", limits.get("ai_requests_per_day", 0))

        # -1 means unlimited
        if ai_limit == -1:
            return True

        if usage.ai_requests >= ai_limit:
            # Calculate time until next reset (midnight UTC)
            now = datetime.now(timezone.utc)
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            seconds_remaining = int((tomorrow - now).total_seconds())
            hours = seconds_remaining // 3600
            minutes = (seconds_remaining % 3600) // 60

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Daily AI request limit exhausted ({usage.ai_requests}/{ai_limit}). "
                    f"Limit resets in {hours}h {minutes}m. Upgrade your plan for more."
                ),
                headers={"Retry-After": str(seconds_remaining)},
            )

        return True

    @staticmethod
    async def check_alert_limit(user_id: int, db: AsyncSession) -> bool:  # noqa: S3516
        """
        Check if user can create more alerts.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if allowed, raises HTTPException if limit exceeded
        """
        from app.models.alert import Alert

        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)

        alert_limit = limits["alerts_max"]

        # -1 means unlimited
        if alert_limit == -1:
            return True

        # Count user's active alerts
        result = await db.execute(
            select(Alert).where(Alert.user_id == user_id, Alert.is_active.is_(True))
        )
        alert_count = len(result.scalars().all())

        if alert_count >= alert_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Alert limit reached ({alert_limit} alerts). Upgrade to create more alerts.",
            )

        return True

    @staticmethod
    async def increment_ai_usage(user_id: int, db: AsyncSession):
        """
        Increment AI request counter for user.

        Args:
            user_id: User ID
            db: Database session
        """
        usage = await TierService.get_or_create_usage(user_id, db)
        usage.ai_requests += 1
        await db.commit()

    @staticmethod
    async def increment_api_usage(user_id: int, db: AsyncSession):
        """
        Increment API call counter for user.

        Args:
            user_id: User ID
            db: Database session
        """
        usage = await TierService.get_or_create_usage(user_id, db)
        usage.api_calls += 1
        await db.commit()

    @staticmethod
    async def check_historical_data_access(
        user_id: int, requested_days: int, db: AsyncSession
    ) -> int:
        """
        Check if user can access historical data for requested days.

        Args:
            user_id: User ID
            requested_days: Number of days user wants to access
            db: Database session

        Returns:
            Max allowed days for user's tier (-1 for unlimited)

        Raises:
            HTTPException(403) if requested days exceed limit
        """
        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)
        max_days = limits["historical_data_days"]

        # -1 means unlimited
        if max_days == -1:
            return -1

        if requested_days > max_days:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Historical data access limited to {max_days} days for {tier} "
                    f"tier. Requested: {requested_days} days. Upgrade to Pro or "
                    "Enterprise for unlimited access."
                ),
            )

        return max_days

    @staticmethod
    async def check_real_time_access(user_id: int, db: AsyncSession) -> bool:
        """
        Check if user has access to real-time updates.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if user has real-time access

        Raises:
            HTTPException(403) if access denied
        """
        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)

        if not limits["real_time_updates"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Real-time updates require Plus tier or higher. Upgrade at "
                    "/pricing to enable real-time data streaming."
                ),
            )

        return True

    @staticmethod
    async def check_api_access(user_id: int, db: AsyncSession) -> bool:
        """
        Check if user has API access.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if user has API access

        Raises:
            HTTPException(403) if access denied
        """
        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)

        if not limits["api_access"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "API access requires Pro tier or higher. Upgrade at /pricing "
                    "to enable API access."
                ),
            )

        return True

    @staticmethod
    async def check_companies_tracked_limit(  # noqa: S3516
        user_id: int, current_count: int, db: AsyncSession
    ) -> bool:
        """
        Check if user can track more companies.

        Args:
            user_id: User ID
            current_count: Current number of companies being tracked
            db: Database session

        Returns:
            True if user can track more companies

        Raises:
            HTTPException(403) if limit exceeded
        """
        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)
        max_companies = limits["companies_tracked"]

        # -1 means unlimited
        if max_companies == -1:
            return True

        if current_count >= max_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Company tracking limit reached ({max_companies} companies for "
                    f"{tier} tier). Upgrade to Pro or Enterprise for unlimited tracking."
                ),
            )

        return True

    @staticmethod
    async def get_usage_stats(user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Get user's current usage stats and limits.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Dictionary with usage stats and limits
        """
        tier = await TierService.get_user_tier(user_id, db)
        limits = await TierService.get_tier_limits(tier)
        usage = await TierService.get_or_create_usage(user_id, db)

        return {
            "tier": tier,
            "limits": limits,
            "usage": {
                "ai_requests": usage.ai_requests,
                "alerts_triggered": usage.alerts_triggered,
                "api_calls": usage.api_calls,
                "companies_viewed": usage.companies_viewed,
            },
            "remaining": {
                "ai_requests": limits.get("ai_requests_limit", limits.get("ai_requests_per_day", 0)) - usage.ai_requests
                if limits.get("ai_requests_limit", limits.get("ai_requests_per_day", 0)) != -1
                else -1,
            },
        }
