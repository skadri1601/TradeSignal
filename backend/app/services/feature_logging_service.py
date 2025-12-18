"""
Service for logging feature access attempts.

Tracks feature usage for analytics and billing purposes.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.feature_usage_log import FeatureUsageLog
from app.services.tier_service import TierService

logger = logging.getLogger(__name__)


class FeatureLoggingService:
    """Service for logging feature access attempts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_feature_access(
        self,
        user_id: int,
        feature_key: str,
        feature_name: Optional[str] = None,
        access_granted: bool = False,
        request: Optional[Request] = None,
    ):
        """
        Log a feature access attempt.

        Args:
            user_id: User ID attempting to access the feature
            feature_key: Key identifying the feature
            feature_name: Human-readable feature name
            access_granted: Whether access was granted
            request: FastAPI Request object for metadata
        """
        try:
            # Get user tier
            user_tier = await TierService.get_user_tier(user_id, self.db)
            limits = await TierService.get_tier_limits(user_tier)

            # Determine required tier
            tier_required = None
            tier_hierarchy = {
                "free": 0,
                "basic": 1,
                "plus": 2,
                "pro": 3,
                "enterprise": 4,
            }

            # Check which tier has this feature
            for tier in ["enterprise", "pro", "plus", "basic", "free"]:
                tier_limits = await TierService.get_tier_limits(tier)
                if tier_limits.get(feature_key, False):
                    tier_required = tier
                    break

            # Extract request metadata
            request_path = None
            request_method = None
            ip_address = None
            user_agent = None

            if request:
                request_path = str(request.url.path)
                request_method = request.method
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")

            # Create log entry
            log_entry = FeatureUsageLog(
                user_id=user_id,
                feature_key=feature_key,
                feature_name=feature_name or feature_key.replace("_", " ").title(),
                tier_required=tier_required,
                user_tier=user_tier,
                access_granted=access_granted,
                request_path=request_path,
                request_method=request_method,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self.db.add(log_entry)
            await self.db.commit()

        except Exception as e:
            # Don't fail the request if logging fails
            logger.error(f"Error logging feature access: {e}", exc_info=True)
            # Rollback to avoid leaving transaction in bad state
            await self.db.rollback()

