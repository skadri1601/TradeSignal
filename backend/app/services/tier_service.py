"""
Tier limit enforcement service.

Checks user subscription tier and enforces usage limits.
"""

from datetime import date
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
                UsageTracking.user_id == user_id,
                UsageTracking.date == today
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
    async def check_ai_limit(user_id: int, db: AsyncSession) -> bool:
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

        ai_limit = limits["ai_requests_per_day"]

        # -1 means unlimited
        if ai_limit == -1:
            return True

        if usage.ai_requests >= ai_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily AI request limit exceeded ({ai_limit} requests). Upgrade to get more requests."
            )

        return True

    @staticmethod
    async def check_alert_limit(user_id: int, db: AsyncSession) -> bool:
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
            select(Alert).where(Alert.user_id == user_id, Alert.is_active == True)
        )
        alert_count = len(result.scalars().all())

        if alert_count >= alert_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Alert limit reached ({alert_limit} alerts). Upgrade to create more alerts."
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
                "ai_requests": limits["ai_requests_per_day"] - usage.ai_requests if limits["ai_requests_per_day"] != -1 else -1,
            }
        }
