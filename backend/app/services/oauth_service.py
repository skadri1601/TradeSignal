"""
OAuth Service for Brokerage Integrations

Handles OAuth 2.0 authentication flows for:
- Alpaca
- TD Ameritrade
- Interactive Brokers

Features:
- CSRF protection via state parameter
- Token encryption at rest (Fernet)
- Token refresh automation
- Secure token revocation
"""

import secrets
import json
import logging
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.brokerage import BrokerageAccount

logger = logging.getLogger(__name__)

BrokerType = Literal["alpaca", "td_ameritrade", "interactive_brokers"]


# ============================================================================
# TOKEN ENCRYPTION
# ============================================================================


class TokenEncryption:
    """Encrypt/decrypt OAuth tokens using Fernet symmetric encryption."""

    def __init__(self, key: str):
        """Initialize with encryption key from settings."""
        self.fernet = Fernet(key.encode())

    def encrypt(self, token: str) -> str:
        """Encrypt a token."""
        return self.fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token."""
        return self.fernet.decrypt(encrypted_token.encode()).decode()


# ============================================================================
# BROKER OAUTH SERVICE
# ============================================================================


class BrokerOAuthService:
    """Handles OAuth flows for all supported brokers."""

    def __init__(self):
        """Initialize OAuth service with encryption."""
        if not settings.token_encryption_key:
            raise ValueError("TOKEN_ENCRYPTION_KEY must be set in environment")
        self.encryption = TokenEncryption(settings.token_encryption_key)
        self._state_tokens: Dict[str, Dict[str, Any]] = {}  # In-memory state storage

    # ========================================================================
    # STATE TOKEN MANAGEMENT (CSRF Protection)
    # ========================================================================

    def generate_state_token(self, user_id: int, broker: BrokerType) -> str:
        """Generate a unique state token for CSRF protection."""
        state = secrets.token_urlsafe(32)
        self._state_tokens[state] = {
            "user_id": user_id,
            "broker": broker,
            "created_at": datetime.utcnow(),
        }
        return state

    def validate_state_token(self, state: str) -> Optional[Dict[str, Any]]:
        """Validate state token and return associated data."""
        if state not in self._state_tokens:
            logger.warning(f"Invalid state token: {state}")
            return None

        token_data = self._state_tokens[state]

        # Check if token expired (15 minute timeout)
        if datetime.utcnow() - token_data["created_at"] > timedelta(minutes=15):
            logger.warning(f"Expired state token: {state}")
            del self._state_tokens[state]
            return None

        # Token is valid, delete it (one-time use)
        del self._state_tokens[state]
        return token_data

    # ========================================================================
    # ALPACA OAUTH
    # ========================================================================

    def get_alpaca_auth_url(self, user_id: int, redirect_uri: Optional[str] = None) -> Dict[str, str]:
        """Generate Alpaca OAuth authorization URL."""
        state = self.generate_state_token(user_id, "alpaca")
        redirect = redirect_uri or settings.alpaca_redirect_uri

        params = {
            "response_type": "code",
            "client_id": settings.alpaca_oauth_client_id,
            "redirect_uri": redirect,
            "state": state,
            "scope": "account:write trading",
        }

        auth_url = f"https://app.alpaca.markets/oauth/authorize?{urlencode(params)}"
        return {"authorization_url": auth_url, "state": state}

    async def handle_alpaca_callback(
        self,
        code: str,
        state: str,
        db: AsyncSession,
        redirect_uri: Optional[str] = None,
    ) -> BrokerageAccount:
        """Handle Alpaca OAuth callback and create brokerage account."""
        # Validate state token
        state_data = self.validate_state_token(state)
        if not state_data:
            raise ValueError("Invalid or expired state token")

        user_id = state_data["user_id"]
        redirect = redirect_uri or settings.alpaca_redirect_uri

        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.alpaca.markets/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.alpaca_oauth_client_id,
                    "client_secret": settings.alpaca_oauth_client_secret,
                    "redirect_uri": redirect,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        # Get account info
        access_token = token_data["access_token"]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.alpaca.markets/v2/account",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            account_info = response.json()

        # Encrypt tokens
        encrypted_access = self.encryption.encrypt(access_token)
        encrypted_refresh = self.encryption.encrypt(token_data.get("refresh_token", ""))

        # Create or update brokerage account
        stmt = select(BrokerageAccount).where(
            BrokerageAccount.user_id == user_id,
            BrokerageAccount.broker == "alpaca",
            BrokerageAccount.account_number == account_info["account_number"],
        )
        result = await db.execute(stmt)
        existing_account = result.scalar_one_or_none()

        if existing_account:
            # Update existing account
            existing_account.access_token = encrypted_access
            existing_account.refresh_token = encrypted_refresh
            existing_account.token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_data.get("expires_in", 3600)
            )
            existing_account.is_active = True
            existing_account.last_synced_at = datetime.utcnow()
            account = existing_account
        else:
            # Create new account
            account = BrokerageAccount(
                user_id=user_id,
                broker="alpaca",
                account_number=account_info["account_number"],
                account_name=f"Alpaca - {account_info['account_number'][-4:]}",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                is_active=True,
                balance=float(account_info.get("cash", 0)),
                buying_power=float(account_info.get("buying_power", 0)),
                portfolio_value=float(account_info.get("portfolio_value", 0)),
                last_synced_at=datetime.utcnow(),
            )
            db.add(account)

        await db.commit()
        await db.refresh(account)
        return account

    # ========================================================================
    # TD AMERITRADE OAUTH
    # ========================================================================

    def get_td_ameritrade_auth_url(self, user_id: int, redirect_uri: Optional[str] = None) -> Dict[str, str]:
        """Generate TD Ameritrade OAuth authorization URL."""
        state = self.generate_state_token(user_id, "td_ameritrade")
        redirect = redirect_uri or settings.td_ameritrade_redirect_uri

        params = {
            "response_type": "code",
            "client_id": f"{settings.td_ameritrade_client_id}@AMER.OAUTHAP",
            "redirect_uri": redirect,
            "state": state,
        }

        auth_url = f"https://auth.tdameritrade.com/auth?{urlencode(params)}"
        return {"authorization_url": auth_url, "state": state}

    async def handle_td_ameritrade_callback(
        self,
        code: str,
        state: str,
        db: AsyncSession,
        redirect_uri: Optional[str] = None,
    ) -> BrokerageAccount:
        """Handle TD Ameritrade OAuth callback and create brokerage account."""
        # Validate state token
        state_data = self.validate_state_token(state)
        if not state_data:
            raise ValueError("Invalid or expired state token")

        user_id = state_data["user_id"]
        redirect = redirect_uri or settings.td_ameritrade_redirect_uri

        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tdameritrade.com/v1/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.td_ameritrade_client_id,
                    "redirect_uri": redirect,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

        # Get account info
        access_token = token_data["access_token"]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.tdameritrade.com/v1/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            accounts = response.json()

        # Use first account
        account_info = accounts[0]["securitiesAccount"]

        # Encrypt tokens
        encrypted_access = self.encryption.encrypt(access_token)
        encrypted_refresh = self.encryption.encrypt(token_data.get("refresh_token", ""))

        # Create or update brokerage account
        stmt = select(BrokerageAccount).where(
            BrokerageAccount.user_id == user_id,
            BrokerageAccount.broker == "td_ameritrade",
            BrokerageAccount.account_number == account_info["accountId"],
        )
        result = await db.execute(stmt)
        existing_account = result.scalar_one_or_none()

        if existing_account:
            # Update existing account
            existing_account.access_token = encrypted_access
            existing_account.refresh_token = encrypted_refresh
            existing_account.token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_data.get("expires_in", 1800)
            )
            existing_account.is_active = True
            existing_account.last_synced_at = datetime.utcnow()
            account = existing_account
        else:
            # Create new account
            account = BrokerageAccount(
                user_id=user_id,
                broker="td_ameritrade",
                account_number=account_info["accountId"],
                account_name=f"TD Ameritrade - {account_info['accountId'][-4:]}",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 1800)),
                is_active=True,
                balance=float(account_info["currentBalances"].get("cashBalance", 0)),
                buying_power=float(account_info["currentBalances"].get("buyingPower", 0)),
                portfolio_value=float(account_info["currentBalances"].get("liquidationValue", 0)),
                last_synced_at=datetime.utcnow(),
            )
            db.add(account)

        await db.commit()
        await db.refresh(account)
        return account

    # ========================================================================
    # INTERACTIVE BROKERS OAUTH
    # ========================================================================

    def get_interactive_brokers_auth_url(self, user_id: int, redirect_uri: Optional[str] = None) -> Dict[str, str]:
        """Generate Interactive Brokers OAuth authorization URL."""
        state = self.generate_state_token(user_id, "interactive_brokers")
        redirect = redirect_uri or settings.ib_redirect_uri

        params = {
            "response_type": "code",
            "client_id": settings.ib_client_id,
            "redirect_uri": redirect,
            "state": state,
            "scope": "read write",
        }

        auth_url = f"https://api.ibkr.com/v1/oauth2/authorize?{urlencode(params)}"
        return {"authorization_url": auth_url, "state": state}

    async def handle_interactive_brokers_callback(
        self,
        code: str,
        state: str,
        db: AsyncSession,
        redirect_uri: Optional[str] = None,
    ) -> BrokerageAccount:
        """Handle Interactive Brokers OAuth callback and create brokerage account."""
        # Validate state token
        state_data = self.validate_state_token(state)
        if not state_data:
            raise ValueError("Invalid or expired state token")

        user_id = state_data["user_id"]
        redirect = redirect_uri or settings.ib_redirect_uri

        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.ibkr.com/v1/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.ib_client_id,
                    "redirect_uri": redirect,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        # Get account info
        access_token = token_data["access_token"]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.ibkr.com/v1/portfolio/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            accounts = response.json()

        # Use first account
        account_number = accounts[0] if isinstance(accounts, list) else accounts["id"]

        # Encrypt tokens
        encrypted_access = self.encryption.encrypt(access_token)
        encrypted_refresh = self.encryption.encrypt(token_data.get("refresh_token", ""))

        # Create or update brokerage account
        stmt = select(BrokerageAccount).where(
            BrokerageAccount.user_id == user_id,
            BrokerageAccount.broker == "interactive_brokers",
            BrokerageAccount.account_number == account_number,
        )
        result = await db.execute(stmt)
        existing_account = result.scalar_one_or_none()

        if existing_account:
            # Update existing account
            existing_account.access_token = encrypted_access
            existing_account.refresh_token = encrypted_refresh
            existing_account.token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_data.get("expires_in", 3600)
            )
            existing_account.is_active = True
            existing_account.last_synced_at = datetime.utcnow()
            account = existing_account
        else:
            # Create new account
            account = BrokerageAccount(
                user_id=user_id,
                broker="interactive_brokers",
                account_number=account_number,
                account_name=f"Interactive Brokers - {account_number[-4:]}",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                is_active=True,
                last_synced_at=datetime.utcnow(),
            )
            db.add(account)

        await db.commit()
        await db.refresh(account)
        return account

    # ========================================================================
    # TOKEN REFRESH
    # ========================================================================

    async def refresh_tokens(self, account: BrokerageAccount, db: AsyncSession) -> None:
        """Refresh OAuth tokens for a brokerage account."""
        if not account.refresh_token:
            raise ValueError("No refresh token available")

        # Decrypt refresh token
        refresh_token = self.encryption.decrypt(account.refresh_token)

        # Refresh based on broker
        if account.broker == "alpaca":
            await self._refresh_alpaca_token(account, refresh_token, db)
        elif account.broker == "td_ameritrade":
            await self._refresh_td_ameritrade_token(account, refresh_token, db)
        elif account.broker == "interactive_brokers":
            await self._refresh_ib_token(account, refresh_token, db)
        else:
            raise ValueError(f"Unsupported broker: {account.broker}")

    async def _refresh_alpaca_token(self, account: BrokerageAccount, refresh_token: str, db: AsyncSession) -> None:
        """Refresh Alpaca access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.alpaca.markets/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.alpaca_oauth_client_id,
                    "client_secret": settings.alpaca_oauth_client_secret,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        # Update account
        account.access_token = self.encryption.encrypt(token_data["access_token"])
        account.refresh_token = self.encryption.encrypt(token_data.get("refresh_token", refresh_token))
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        await db.commit()

    async def _refresh_td_ameritrade_token(self, account: BrokerageAccount, refresh_token: str, db: AsyncSession) -> None:
        """Refresh TD Ameritrade access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tdameritrade.com/v1/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.td_ameritrade_client_id,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

        # Update account
        account.access_token = self.encryption.encrypt(token_data["access_token"])
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 1800))
        await db.commit()

    async def _refresh_ib_token(self, account: BrokerageAccount, refresh_token: str, db: AsyncSession) -> None:
        """Refresh Interactive Brokers access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.ibkr.com/v1/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.ib_client_id,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        # Update account
        account.access_token = self.encryption.encrypt(token_data["access_token"])
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        await db.commit()

    # ========================================================================
    # TOKEN REVOCATION
    # ========================================================================

    async def revoke_tokens(self, account: BrokerageAccount, db: AsyncSession) -> None:
        """Revoke OAuth tokens and deactivate account."""
        try:
            # Decrypt access token
            access_token = self.encryption.decrypt(account.access_token)

            # Revoke based on broker
            if account.broker == "alpaca":
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "https://api.alpaca.markets/oauth/revoke",
                        data={"token": access_token},
                    )
            elif account.broker == "td_ameritrade":
                # TD Ameritrade doesn't have a revoke endpoint, just deactivate
                pass
            elif account.broker == "interactive_brokers":
                # IB doesn't have a revoke endpoint, just deactivate
                pass

        except Exception as e:
            logger.warning(f"Failed to revoke tokens for {account.broker}: {e}")

        # Deactivate account
        account.is_active = False
        account.access_token = None
        account.refresh_token = None
        account.token_expires_at = None
        await db.commit()


# Global service instance
oauth_service = BrokerOAuthService()
