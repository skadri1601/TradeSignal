"""
Feature gating middleware for subscription tier enforcement.

Checks user subscription tier and blocks access to premium features
if user doesn't have required tier.
"""

import logging
from typing import Callable, Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subscription import SubscriptionTier, TIER_LIMITS
from app.services.tier_service import TierService

logger = logging.getLogger(__name__)

# Tier hierarchy for comparison (higher number = higher tier)
TIER_HIERARCHY = {
    SubscriptionTier.FREE.value: 0,
    SubscriptionTier.BASIC.value: 1,
    SubscriptionTier.PLUS.value: 2,
    SubscriptionTier.PRO.value: 3,
    SubscriptionTier.ENTERPRISE.value: 4,
}


# PORTFOLIO MODE: Set to True to bypass all tier checks (for portfolio showcase)
PORTFOLIO_MODE = True


def require_tier(
    min_tier: str,
    feature_name: Optional[str] = None,
    upgrade_message: Optional[str] = None,
):
    """
    Dependency factory for requiring a minimum subscription tier.

    Args:
        min_tier: Minimum tier required (free, basic, plus, pro, enterprise)
        feature_name: Name of the feature being accessed (for error messages)
        upgrade_message: Custom upgrade message

    Returns:
        Dependency function that checks tier and raises HTTPException if insufficient
    """
    min_tier_lower = min_tier.lower()
    min_tier_level = TIER_HIERARCHY.get(min_tier_lower, 0)

    async def check_tier(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """Check if user has required tier."""
        # PORTFOLIO MODE: Skip all tier checks
        if PORTFOLIO_MODE:
            return current_user

        # Get user's current tier
        user_tier = await TierService.get_user_tier(current_user.id, db)
        user_tier_level = TIER_HIERARCHY.get(user_tier, 0)

        if user_tier_level < min_tier_level:
            feature_desc = feature_name or "This feature"
            default_message = (
                f"{feature_desc} requires a {min_tier.upper()} subscription or higher. "
                f"Your current tier is {user_tier.upper()}. "
                "Please upgrade your plan to access this feature."
            )
            message = upgrade_message or default_message

            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "subscription_required",
                    "message": message,
                    "required_tier": min_tier_lower,
                    "current_tier": user_tier,
                    "feature": feature_name,
                    "upgrade_url": "/pricing",
                },
            )

        return current_user

    return check_tier


def require_feature(
    feature_key: str,
    feature_name: Optional[str] = None,
):
    """
    Dependency factory for requiring a specific feature.

    Args:
        feature_key: Key in TIER_LIMITS to check (e.g., 'api_access', 'export_enabled')
        feature_name: Human-readable name of the feature

    Returns:
        Dependency function that checks feature access
    """
    async def check_feature(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """Check if user's tier has access to the feature."""
        # PORTFOLIO MODE: Skip all feature checks
        if PORTFOLIO_MODE:
            return current_user

        user_tier = await TierService.get_user_tier(current_user.id, db)
        limits = await TierService.get_tier_limits(user_tier)

        has_feature = limits.get(feature_key, False)

        if not has_feature:
            feature_desc = feature_name or feature_key.replace("_", " ").title()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "feature_not_available",
                    "message": (
                        f"{feature_desc} is not available for {user_tier.upper()} tier. "
                        "Please upgrade your plan to access this feature."
                    ),
                    "feature": feature_key,
                    "current_tier": user_tier,
                    "upgrade_url": "/pricing",
                },
            )

        return current_user

    return check_feature


async def feature_gating_middleware(
    request: Request,
    call_next: Callable,
):
    """
    Middleware to check feature access for all requests.

    This is a global middleware that can be used to add feature gating
    headers or perform additional checks. For route-level gating, use
    the dependency functions above.
    """
    response = await call_next(request)

    # Add user tier info to response headers (for frontend)
    if "user" in request.state:
        user: User = request.state.user
        # Note: This requires user to be set in request state by auth middleware
        # For now, we'll rely on dependency injection for tier checks

    return response

