"""
Brokerage Integration Service.

OAuth with broker APIs, account linking, trade execution, copy trading.
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.brokerage import (
    BrokerageAccount,
    CopyTradeRule,
    ExecutedTrade,
)
from app.services.broker_clients import get_broker_client
from app.services.oauth_service import oauth_service

logger = logging.getLogger(__name__)


class BrokerageService:
    """Service for brokerage integration and copy trading."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def connect_brokerage_account(
        self,
        user_id: int,
        brokerage_name: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> BrokerageAccount:
        """
        Connect a brokerage account via OAuth.

        Stores OAuth tokens for API access.
        """
        # Check if account already exists
        result = await self.db.execute(
            select(BrokerageAccount).where(
                BrokerageAccount.user_id == user_id,
                BrokerageAccount.brokerage_name == brokerage_name,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing connection
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.token_expires_at = datetime.utcnow() + timedelta(days=90)  # Typical expiry
            existing.is_active = True
            existing.last_synced_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(existing)

            return existing

        # Create new connection
        account = BrokerageAccount(
            user_id=user_id,
            brokerage_name=brokerage_name,
            account_id=account_id or f"account_{user_id}_{int(datetime.utcnow().timestamp())}",
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=datetime.utcnow() + timedelta(days=90),
            is_verified=False,  # Would verify via API call
        )
        self.db.add(account)

        # Verify account by fetching account info
        try:
            account_info = await self._fetch_account_info(account)
            if account_info:
                account.is_verified = True
                account.account_balance = account_info.get("balance")
                account.buying_power = account_info.get("buying_power")
                account.last_synced_at = datetime.utcnow()
        except Exception as e:
            logger.warning(f"Could not verify brokerage account: {e}")

        await self.db.commit()
        await self.db.refresh(account)

        return account

    async def _fetch_account_info(self, account: BrokerageAccount) -> Optional[Dict[str, Any]]:
        """
        Fetch account information from brokerage API using broker clients.
        """
        try:
            # Decrypt access token
            access_token = oauth_service.encryption.decrypt(account.access_token)

            # Get broker client
            broker_client = get_broker_client(account.broker, access_token)

            # Fetch account info
            account_info = await broker_client.get_account_info()

            return account_info
        except Exception as e:
            logger.error(f"Error fetching account info for {account.broker}: {e}")
            return None

    async def create_copy_trade_rule(
        self,
        user_id: int,
        brokerage_account_id: int,
        rule_name: str,
        source_type: str,
        source_filter: Optional[Dict[str, Any]] = None,
        position_size_type: str = "percentage",
        position_size_value: float = 5.0,  # 5% of portfolio
        max_position_size: Optional[float] = None,
        max_daily_trades: Optional[int] = None,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None,
    ) -> CopyTradeRule:
        """Create a copy trading rule."""
        # Verify brokerage account belongs to user
        result = await self.db.execute(
            select(BrokerageAccount).where(
                BrokerageAccount.id == brokerage_account_id,
                BrokerageAccount.user_id == user_id,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            raise ValueError("Brokerage account not found or access denied")

        if not account.is_active:
            raise ValueError("Brokerage account is not active")

        rule = CopyTradeRule(
            user_id=user_id,
            brokerage_account_id=brokerage_account_id,
            rule_name=rule_name,
            source_type=source_type,
            source_filter=source_filter,
            position_size_type=position_size_type,
            position_size_value=position_size_value,
            max_position_size=max_position_size,
            max_daily_trades=max_daily_trades,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)

        return rule

    async def execute_copy_trade(
        self,
        rule_id: int,
        ticker: str,
        transaction_type: str,
        source_trade_id: Optional[int] = None,
        source_politician_trade_id: Optional[int] = None,
    ) -> ExecutedTrade:
        """
        Execute a copy trade through brokerage API.

        Creates order and tracks execution.
        """
        # Get rule
        rule = await self.db.get(CopyTradeRule, rule_id)
        if not rule or not rule.is_active:
            raise ValueError("Copy trade rule not found or inactive")

        # Get brokerage account
        account = await self.db.get(BrokerageAccount, rule.brokerage_account_id)
        if not account or not account.is_active:
            raise ValueError("Brokerage account not found or inactive")

        # Calculate position size
        shares, total_value = await self._calculate_position_size(rule, account, ticker)

        # Get current price from broker API
        current_price = await self._get_current_price(account, ticker)

        # Create executed trade record
        executed_trade = ExecutedTrade(
            copy_trade_rule_id=rule_id,
            brokerage_account_id=account.id,
            ticker=ticker.upper(),
            transaction_type=transaction_type,
            shares=shares,
            price=current_price,
            total_value=total_value,
            source_trade_id=source_trade_id,
            source_politician_trade_id=source_politician_trade_id,
            execution_status="pending",
        )
        self.db.add(executed_trade)
        await self.db.flush()

        # Execute trade via broker API
        try:
            order_result = await self._place_broker_order(
                account, ticker, transaction_type, Decimal(str(shares))
            )

            status = order_result.get("status", "pending")
            if status == "filled":
                executed_trade.execution_status = "filled"
                executed_trade.broker_order_id = order_result.get("broker_order_id")
                executed_trade.filled_at = datetime.utcnow()
                filled_price = order_result.get("filled_price")
                executed_trade.price = filled_price if filled_price else current_price

                # Update rule statistics
                rule.total_trades_executed += 1
            elif status == "pending":
                executed_trade.execution_status = "pending"
                executed_trade.broker_order_id = order_result.get("broker_order_id")
            else:
                executed_trade.execution_status = "rejected"
                executed_trade.broker_order_id = order_result.get("broker_order_id")

        except Exception as e:
            logger.error(f"Error executing copy trade: {e}", exc_info=True)
            executed_trade.execution_status = "rejected"

        await self.db.commit()
        await self.db.refresh(executed_trade)

        return executed_trade

    async def _calculate_position_size(
        self, rule: CopyTradeRule, account: BrokerageAccount, ticker: str
    ) -> tuple[float, float]:
        """Calculate position size based on rule settings."""
        if not account.buying_power:
            raise ValueError("Account buying power not available")

        buying_power = float(account.buying_power)

        if rule.position_size_type == "percentage":
            position_value = buying_power * (rule.position_size_value / 100)
        elif rule.position_size_type == "fixed_dollar":
            position_value = rule.position_size_value
        else:  # shares
            # Need current price
            current_price = await self._get_current_price(account, ticker)
            position_value = float(rule.position_size_value) * float(current_price)

        # Apply max position size limit
        if rule.max_position_size:
            position_value = min(position_value, float(rule.max_position_size))

        # Get current price
        current_price = await self._get_current_price(account, ticker)
        shares = position_value / float(current_price) if current_price > 0 else 0

        return shares, position_value

    async def _get_current_price(self, account: BrokerageAccount, ticker: str) -> Decimal:
        """Get current stock price from broker API."""
        try:
            # Decrypt access token
            access_token = oauth_service.encryption.decrypt(account.access_token)

            # Get broker client
            broker_client = get_broker_client(account.broker, access_token)

            # Get current price
            price = await broker_client.get_current_price(ticker)

            return price
        except Exception as e:
            logger.error(f"Error fetching price for {ticker} from {account.broker}: {e}")
            raise ValueError(f"Could not fetch price for {ticker}")

    async def _place_broker_order(
        self,
        account: BrokerageAccount,
        ticker: str,
        transaction_type: str,
        shares: Decimal,
        order_type: str = "market",
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        time_in_force: str = "day",
    ) -> Dict[str, Any]:
        """
        Place order via broker API using broker clients.
        """
        try:
            # Decrypt access token
            access_token = oauth_service.encryption.decrypt(account.access_token)

            # Get broker client
            broker_client = get_broker_client(account.broker, access_token)

            # Place order
            order_result = await broker_client.place_order(
                ticker=ticker,
                side=transaction_type.lower(),  # 'buy' or 'sell'
                quantity=shares,
                order_type=order_type,
                limit_price=limit_price,
                stop_price=stop_price,
                time_in_force=time_in_force,
            )

            return order_result
        except Exception as e:
            logger.error(f"Error placing order for {ticker} on {account.broker}: {e}")
            raise

    async def get_user_brokerage_accounts(self, user_id: int) -> List[BrokerageAccount]:
        """Get all brokerage accounts for a user."""
        result = await self.db.execute(
            select(BrokerageAccount).where(
                BrokerageAccount.user_id == user_id,
                BrokerageAccount.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def get_copy_trade_rules(self, user_id: int) -> List[CopyTradeRule]:
        """Get all copy trade rules for a user."""
        result = await self.db.execute(
            select(CopyTradeRule).where(CopyTradeRule.user_id == user_id)
        )
        return list(result.scalars().all())

