"""
Tests for tier limit enforcement service.
Phase 6: Testing tier limits and subscription logic.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.tier_service import TierService
from app.models.subscription import Subscription, SubscriptionTier
from app.models.usage import UsageTracking
from app.models.user import User


@pytest.mark.asyncio
async def test_get_user_tier_free_default(test_db: AsyncSession):
    """Test that users without subscription default to free tier."""
    # Create user without subscription
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    tier = await TierService.get_user_tier(user.id, test_db)
    assert tier == SubscriptionTier.FREE.value


@pytest.mark.asyncio
async def test_get_user_tier_pro(test_db: AsyncSession):
    """Test getting pro tier for subscribed user."""
    # Create user with pro subscription
    user = User(
        email="pro@example.com",
        username="prouser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.PRO.value,
        is_active=True
    )
    test_db.add(subscription)
    await test_db.commit()

    tier = await TierService.get_user_tier(user.id, test_db)
    assert tier == SubscriptionTier.PRO.value


@pytest.mark.asyncio
async def test_get_tier_limits_free(test_db: AsyncSession):
    """Test free tier limits."""
    limits = await TierService.get_tier_limits(SubscriptionTier.FREE.value)

    assert limits["ai_requests_per_day"] == 5
    assert limits["alerts_max"] == 3
    assert limits["real_time_updates"] is False
    assert limits["api_access"] is False


@pytest.mark.asyncio
async def test_get_tier_limits_enterprise(test_db: AsyncSession):
    """Test enterprise tier limits."""
    limits = await TierService.get_tier_limits(SubscriptionTier.ENTERPRISE.value)

    assert limits["ai_requests_per_day"] == -1  # Unlimited
    assert limits["alerts_max"] == -1  # Unlimited
    assert limits["real_time_updates"] is True
    assert limits["api_access"] is True


@pytest.mark.asyncio
async def test_check_ai_limit_within_quota(test_db: AsyncSession):
    """Test AI limit check when user is within quota."""
    # Create user with free tier (5 requests/day)
    user = User(
        email="ai@example.com",
        username="aiuser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    # Create usage with 3 requests (under limit)
    usage = UsageTracking(
        user_id=user.id,
        date=date.today(),
        ai_requests=3
    )
    test_db.add(usage)
    await test_db.commit()

    # Should pass
    result = await TierService.check_ai_limit(user.id, test_db)
    assert result is True


@pytest.mark.asyncio
async def test_check_ai_limit_exceeded(test_db: AsyncSession):
    """Test AI limit check when user exceeds quota."""
    # Create user with free tier (5 requests/day)
    user = User(
        email="overlimit@example.com",
        username="overlimituser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    # Create usage with 5 requests (at limit)
    usage = UsageTracking(
        user_id=user.id,
        date=date.today(),
        ai_requests=5
    )
    test_db.add(usage)
    await test_db.commit()

    # Should raise exception
    with pytest.raises(HTTPException) as exc_info:
        await TierService.check_ai_limit(user.id, test_db)

    assert exc_info.value.status_code == 429
    assert "limit exceeded" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_check_ai_limit_unlimited(test_db: AsyncSession):
    """Test AI limit check for enterprise tier with unlimited requests."""
    # Create user with enterprise tier
    user = User(
        email="enterprise@example.com",
        username="enterpriseuser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.ENTERPRISE.value,
        is_active=True
    )
    test_db.add(subscription)
    await test_db.commit()

    # Create usage with 1000 requests
    usage = UsageTracking(
        user_id=user.id,
        date=date.today(),
        ai_requests=1000
    )
    test_db.add(usage)
    await test_db.commit()

    # Should still pass (unlimited)
    result = await TierService.check_ai_limit(user.id, test_db)
    assert result is True


@pytest.mark.asyncio
async def test_increment_ai_usage(test_db: AsyncSession):
    """Test incrementing AI usage counter."""
    # Create user
    user = User(
        email="increment@example.com",
        username="incrementuser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    # Increment usage
    await TierService.increment_ai_usage(user.id, test_db)

    # Check usage was created and incremented
    usage = await TierService.get_or_create_usage(user.id, test_db)
    assert usage.ai_requests == 1

    # Increment again
    await TierService.increment_ai_usage(user.id, test_db)

    # Refresh and check
    await test_db.refresh(usage)
    assert usage.ai_requests == 2


@pytest.mark.asyncio
async def test_get_usage_stats(test_db: AsyncSession):
    """Test getting comprehensive usage statistics."""
    # Create user with basic tier
    user = User(
        email="stats@example.com",
        username="statsuser",
        hashed_password="fakehash"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.BASIC.value,
        is_active=True
    )
    test_db.add(subscription)
    await test_db.commit()

    # Create usage
    usage = UsageTracking(
        user_id=user.id,
        date=date.today(),
        ai_requests=10,
        api_calls=50,
        alerts_triggered=5
    )
    test_db.add(usage)
    await test_db.commit()

    # Get stats
    stats = await TierService.get_usage_stats(user.id, test_db)

    assert stats["tier"] == SubscriptionTier.BASIC.value
    assert stats["usage"]["ai_requests"] == 10
    assert stats["usage"]["api_calls"] == 50
    assert stats["usage"]["alerts_triggered"] == 5
    assert stats["remaining"]["ai_requests"] == 40  # Basic tier has 50/day
    assert "limits" in stats
