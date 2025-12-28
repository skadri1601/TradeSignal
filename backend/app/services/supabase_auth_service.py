"""
Supabase Auth Service for gradual migration.

This service handles authentication for new users via Supabase Auth,
while existing users continue using custom JWT auth.
"""

import logging
from typing import Optional
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SupabaseUser:
    """Supabase user data."""
    id: str  # UUID
    email: str
    access_token: str
    refresh_token: str
    expires_in: int  # seconds


@dataclass
class SupabaseTokens:
    """Supabase auth tokens."""
    access_token: str
    refresh_token: str
    expires_in: int


class SupabaseAuthService:
    """
    Service for Supabase Auth operations.

    Used for new user registration and login when auth_provider='supabase'.
    """

    def __init__(self):
        self._client = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of Supabase client."""
        if self._initialized:
            return

        if not settings.supabase_url or not settings.supabase_service_role_key:
            logger.warning(
                "Supabase Auth not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
            self._initialized = True
            return

        try:
            from supabase import create_client, Client
            self._client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
            self._initialized = True
            logger.info("Supabase Auth client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self._initialized = True

    @property
    def is_configured(self) -> bool:
        """Check if Supabase Auth is properly configured."""
        self._ensure_initialized()
        return self._client is not None

    async def create_user(self, email: str, password: str) -> Optional[SupabaseUser]:
        """
        Create a new user in Supabase Auth.

        Args:
            email: User's email address
            password: User's password

        Returns:
            SupabaseUser with id and tokens, or None if failed
        """
        self._ensure_initialized()
        if not self._client:
            logger.error("Supabase client not initialized")
            return None

        try:
            # Create user with email/password
            response = self._client.auth.sign_up({
                "email": email,
                "password": password,
            })

            if response.user and response.session:
                logger.info(f"Created Supabase user: {response.user.id}")
                return SupabaseUser(
                    id=response.user.id,
                    email=response.user.email,
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    expires_in=response.session.expires_in or 3600,
                )
            else:
                logger.error(f"Supabase sign_up failed: no user/session returned")
                return None

        except Exception as e:
            logger.error(f"Failed to create Supabase user: {e}")
            return None

    async def sign_in(self, email: str, password: str) -> Optional[SupabaseTokens]:
        """
        Sign in a user via Supabase Auth.

        Args:
            email: User's email address
            password: User's password

        Returns:
            SupabaseTokens with access and refresh tokens, or None if failed
        """
        self._ensure_initialized()
        if not self._client:
            logger.error("Supabase client not initialized")
            return None

        try:
            response = self._client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

            if response.session:
                return SupabaseTokens(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    expires_in=response.session.expires_in or 3600,
                )
            else:
                logger.warning(f"Supabase sign_in failed for {email}")
                return None

        except Exception as e:
            logger.error(f"Supabase sign_in error: {e}")
            return None

    async def get_user(self, access_token: str) -> Optional[dict]:
        """
        Get user info from Supabase JWT token.

        Args:
            access_token: Supabase JWT access token

        Returns:
            User dict with id and email, or None if invalid
        """
        self._ensure_initialized()
        if not self._client:
            return None

        try:
            response = self._client.auth.get_user(access_token)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                }
            return None
        except Exception as e:
            logger.debug(f"Failed to get Supabase user: {e}")
            return None

    async def refresh_token(self, refresh_token: str) -> Optional[SupabaseTokens]:
        """
        Refresh Supabase auth tokens.

        Args:
            refresh_token: Current refresh token

        Returns:
            New SupabaseTokens, or None if failed
        """
        self._ensure_initialized()
        if not self._client:
            return None

        try:
            response = self._client.auth.refresh_session(refresh_token)
            if response.session:
                return SupabaseTokens(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    expires_in=response.session.expires_in or 3600,
                )
            return None
        except Exception as e:
            logger.error(f"Failed to refresh Supabase token: {e}")
            return None

    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out user from Supabase.

        Args:
            access_token: User's current access token

        Returns:
            True if successful, False otherwise
        """
        self._ensure_initialized()
        if not self._client:
            return False

        try:
            self._client.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Failed to sign out from Supabase: {e}")
            return False


# Global instance
supabase_auth_service = SupabaseAuthService()
