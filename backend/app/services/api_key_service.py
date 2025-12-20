"""
API Key Service

Handles API key creation, validation, rate limiting, and usage tracking.
"""

import logging
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.api_key import UserAPIKey, APIKeyUsage
from app.models.user import User

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing API keys."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_api_key(
        self,
        user_id: int,
        name: str,
        description: Optional[str],
        rate_limit: int,
        permissions: Dict[str, bool],
        expires_at: Optional[datetime],
    ) -> tuple[UserAPIKey, str]:
        """
        Create a new API key.

        Args:
            user_id: User ID who owns the key
            name: Key name/identifier
            description: Optional description
            rate_limit: Requests per hour limit
            permissions: Dict with 'read', 'write', 'delete' permissions
            expires_at: Optional expiration datetime

        Returns:
            tuple: (api_key_record, plaintext_key)
                The plaintext key is only returned once and should be shown to the user immediately.
        """
        # Generate key
        full_key, key_hash, key_prefix = UserAPIKey.generate_key()

        # Create API key record
        api_key = UserAPIKey(
            user_id=user_id,
            name=name,
            description=description,
            key_hash=key_hash,
            key_prefix=key_prefix,
            rate_limit_per_hour=rate_limit,
            can_read=permissions.get("read", True),
            can_write=permissions.get("write", False),
            can_delete=permissions.get("delete", False),
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True,
        )

        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)

        logger.info(f"Created API key {api_key.id} for user {user_id}")

        return (api_key, full_key)

    async def validate_api_key(self, key: str) -> Optional[UserAPIKey]:
        """
        Validate an API key and return the record if valid.

        Args:
            key: Plaintext API key

        Returns:
            UserAPIKey if valid, None otherwise
        """
        # Hash the provided key
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Lookup by hash
        result = await self.db.execute(
            select(UserAPIKey).where(
                and_(
                    UserAPIKey.key_hash == key_hash,
                    UserAPIKey.is_active == True
                )
            )
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return None

        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            logger.warning(f"API key {api_key.id} has expired")
            return None

        # Update last used timestamp
        api_key.last_used_at = datetime.utcnow()
        await self.db.commit()

        return api_key

    async def check_rate_limit(self, api_key_id: int) -> bool:
        """
        Check if API key has exceeded its rate limit.

        Args:
            api_key_id: API key ID

        Returns:
            True if under limit, False if exceeded
        """
        # Get API key
        result = await self.db.execute(
            select(UserAPIKey).where(UserAPIKey.id == api_key_id)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        # Count usage in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        result = await self.db.execute(
            select(func.count(APIKeyUsage.id)).where(
                and_(
                    APIKeyUsage.api_key_id == api_key_id,
                    APIKeyUsage.timestamp >= one_hour_ago
                )
            )
        )
        usage_count = result.scalar_one()

        return usage_count < api_key.rate_limit_per_hour

    async def log_usage(
        self,
        api_key_id: int,
        endpoint: str,
        status_code: int,
        response_time_ms: int,
    ):
        """
        Log API key usage for analytics and rate limiting.

        Args:
            api_key_id: API key ID
            endpoint: API endpoint called
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
        """
        usage = APIKeyUsage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            timestamp=datetime.utcnow(),
            status_code=status_code,
            response_time_ms=response_time_ms,
        )

        self.db.add(usage)
        await self.db.commit()

    async def list_user_keys(self, user_id: int) -> List[UserAPIKey]:
        """
        Get all API keys for a user.

        Args:
            user_id: User ID

        Returns:
            List of UserAPIKey records
        """
        result = await self.db.execute(
            select(UserAPIKey)
            .where(UserAPIKey.user_id == user_id)
            .order_by(UserAPIKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_key(self, api_key_id: int, user_id: int) -> bool:
        """
        Revoke (deactivate) an API key.

        Args:
            api_key_id: API key ID
            user_id: User ID (for verification)

        Returns:
            True if revoked, False if not found or not owned by user
        """
        result = await self.db.execute(
            select(UserAPIKey).where(
                and_(
                    UserAPIKey.id == api_key_id,
                    UserAPIKey.user_id == user_id
                )
            )
        )
        api_key = result.scalar_one_or_none()

        if api_key:
            api_key.is_active = False
            await self.db.commit()
            logger.info(f"Revoked API key {api_key_id} for user {user_id}")
            return True

        return False

    async def get_usage_stats(
        self,
        api_key_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get usage statistics for an API key.

        Args:
            api_key_id: API key ID
            days: Number of days to look back

        Returns:
            Dict with usage statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get total usage count
        result = await self.db.execute(
            select(func.count(APIKeyUsage.id)).where(
                and_(
                    APIKeyUsage.api_key_id == api_key_id,
                    APIKeyUsage.timestamp >= cutoff_date
                )
            )
        )
        total_requests = result.scalar_one() or 0

        # Get success/failure counts
        result = await self.db.execute(
            select(func.count(APIKeyUsage.id)).where(
                and_(
                    APIKeyUsage.api_key_id == api_key_id,
                    APIKeyUsage.timestamp >= cutoff_date,
                    APIKeyUsage.status_code >= 200,
                    APIKeyUsage.status_code < 300
                )
            )
        )
        successful_requests = result.scalar_one() or 0

        # Get average response time
        result = await self.db.execute(
            select(func.avg(APIKeyUsage.response_time_ms)).where(
                and_(
                    APIKeyUsage.api_key_id == api_key_id,
                    APIKeyUsage.timestamp >= cutoff_date
                )
            )
        )
        avg_response_time = result.scalar_one() or 0

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "avg_response_time_ms": float(avg_response_time) if avg_response_time else 0,
            "days": days,
        }

