"""
Copy Trading Celery Tasks

Background tasks for automated copy trading execution and account management.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.database import db_manager
from app.models.brokerage import BrokerageAccount, CopyTradeRule, ExecutedTrade
from app.models.trade import Trade
from app.services.brokerage_service import BrokerageService
from app.services.oauth_service import oauth_service

logger = logging.getLogger(__name__)


# ============================================================================
# COPY TRADE EXECUTION
# ============================================================================


@celery_app.task(name="execute_copy_trade")
def execute_copy_trade_task(rule_id: int, insider_trade_id: int):
    """
    Execute a copy trade for a specific rule and insider trade.

    This task is triggered when a new insider trade matches a copy trade rule.
    """
    import asyncio

    async def _execute():
        async with db_manager.get_session() as db:
            try:
                # Get rule
                rule = await db.get(CopyTradeRule, rule_id)
                if not rule or not rule.is_active:
                    logger.warning(f"Copy trade rule {rule_id} not found or inactive")
                    return

                # Get insider trade
                insider_trade = await db.get(Trade, insider_trade_id)
                if not insider_trade:
                    logger.warning(f"Insider trade {insider_trade_id} not found")
                    return

                # Check if already executed
                stmt = select(ExecutedTrade).where(
                    and_(
                        ExecutedTrade.copy_trade_rule_id == rule_id,
                        ExecutedTrade.source_trade_id == insider_trade_id,
                    )
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"Trade already executed for rule {rule_id} and insider trade {insider_trade_id}")
                    return

                # Check daily trade limit
                if rule.max_daily_trades:
                    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    stmt = select(ExecutedTrade).where(
                        and_(
                            ExecutedTrade.copy_trade_rule_id == rule_id,
                            ExecutedTrade.created_at >= today_start,
                        )
                    )
                    result = await db.execute(stmt)
                    today_trades = len(result.scalars().all())

                    if today_trades >= rule.max_daily_trades:
                        logger.info(f"Daily trade limit reached for rule {rule_id} ({today_trades}/{rule.max_daily_trades})")
                        return

                # Execute the trade
                service = BrokerageService(db)
                executed_trade = await service.execute_copy_trade(
                    rule_id=rule_id,
                    ticker=insider_trade.ticker,
                    transaction_type=insider_trade.transaction_type.lower(),
                    source_trade_id=insider_trade_id,
                )

                logger.info(
                    f"Copy trade executed: Rule {rule_id}, Ticker {insider_trade.ticker}, "
                    f"Status {executed_trade.execution_status}"
                )

                return executed_trade.id

            except Exception as e:
                logger.error(f"Error executing copy trade for rule {rule_id}: {e}", exc_info=True)
                await db.rollback()
                raise

    # Run async function
    return asyncio.run(_execute())


@celery_app.task(name="check_and_execute_copy_trades")
def check_and_execute_copy_trades_task(insider_trade_id: int):
    """
    Check all active copy trade rules and execute matching ones.

    This task is triggered when a new insider trade is added to the system.
    """
    import asyncio

    async def _check_and_execute():
        async with db_manager.get_session() as db:
            try:
                # Get all active copy trade rules
                stmt = select(CopyTradeRule).where(CopyTradeRule.is_active.is_(True))
                result = await db.execute(stmt)
                active_rules = result.scalars().all()

                # Get insider trade
                insider_trade = await db.get(Trade, insider_trade_id)
                if not insider_trade:
                    logger.warning(f"Insider trade {insider_trade_id} not found")
                    return

                # Check each rule
                executed_count = 0
                for rule in active_rules:
                    # Check if trade matches rule conditions
                    if await _matches_rule_conditions(insider_trade, rule):
                        # Queue execution task
                        execute_copy_trade_task.delay(rule.id, insider_trade_id)
                        executed_count += 1

                logger.info(f"Queued {executed_count} copy trades for insider trade {insider_trade_id}")
                return executed_count

            except Exception as e:
                logger.error(f"Error checking copy trade rules: {e}", exc_info=True)
                raise

    return asyncio.run(_check_and_execute())


async def _matches_rule_conditions(insider_trade: Trade, rule: CopyTradeRule) -> bool:
    """
    Check if an insider trade matches a copy trade rule's conditions.
    """
    if not rule.source_filter:
        return True  # No filters = match all

    conditions = rule.source_filter.get("conditions", [])

    for condition in conditions:
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # Get trade field value
        if field == "transaction_type":
            trade_value = insider_trade.transaction_type
        elif field == "security_type":
            trade_value = insider_trade.security_type
        elif field == "share_volume":
            trade_value = insider_trade.shares
        elif field == "transaction_value":
            trade_value = insider_trade.value
        elif field == "ticker":
            trade_value = insider_trade.ticker
        elif field == "insider_title":
            trade_value = getattr(insider_trade, "insider_title", None)
        elif field == "company_sector":
            trade_value = getattr(insider_trade, "company_sector", None)
        else:
            continue  # Unknown field

        # Apply operator
        if operator == "equals":
            if trade_value != value:
                return False
        elif operator == "not_equals":
            if trade_value == value:
                return False
        elif operator == "greater_than":
            if trade_value <= value:
                return False
        elif operator == "less_than":
            if trade_value >= value:
                return False
        elif operator == "contains":
            if value.lower() not in str(trade_value).lower():
                return False
        elif operator == "in":
            if trade_value not in value:
                return False

    return True  # All conditions matched


# ============================================================================
# ACCOUNT SYNCING
# ============================================================================


@celery_app.task(name="sync_brokerage_accounts")
def sync_brokerage_accounts_task():
    """
    Sync all active brokerage accounts with broker APIs.

    Runs periodically (every 5 minutes) to update balances and positions.
    """
    import asyncio

    async def _sync():
        async with db_manager.get_session() as db:
            try:
                # Get all active accounts
                stmt = select(BrokerageAccount).where(BrokerageAccount.is_active.is_(True))
                result = await db.execute(stmt)
                accounts = result.scalars().all()

                synced_count = 0
                error_count = 0

                for account in accounts:
                    try:
                        service = BrokerageService(db)
                        account_info = await service._fetch_account_info(account)

                        if account_info:
                            account.balance = account_info["balance"]
                            account.buying_power = account_info["buying_power"]
                            account.portfolio_value = account_info["portfolio_value"]
                            account.last_synced_at = datetime.utcnow()
                            synced_count += 1
                        else:
                            error_count += 1

                    except Exception as e:
                        logger.error(f"Error syncing account {account.id}: {e}")
                        error_count += 1

                await db.commit()

                logger.info(f"Synced {synced_count} brokerage accounts ({error_count} errors)")
                return {"synced": synced_count, "errors": error_count}

            except Exception as e:
                logger.error(f"Error in sync_brokerage_accounts_task: {e}", exc_info=True)
                await db.rollback()
                raise

    return asyncio.run(_sync())


# ============================================================================
# TOKEN REFRESH
# ============================================================================


@celery_app.task(name="refresh_broker_tokens")
def refresh_broker_tokens_task():
    """
    Refresh OAuth tokens for all brokerage accounts.

    Runs every 6 hours to ensure tokens don't expire.
    """
    import asyncio

    async def _refresh():
        async with db_manager.get_session() as db:
            try:
                # Get accounts with tokens expiring in next 12 hours
                expiry_threshold = datetime.utcnow() + timedelta(hours=12)
                stmt = select(BrokerageAccount).where(
                    and_(
                        BrokerageAccount.is_active.is_(True),
                        BrokerageAccount.token_expires_at <= expiry_threshold,
                    )
                )
                result = await db.execute(stmt)
                accounts = result.scalars().all()

                refreshed_count = 0
                error_count = 0

                for account in accounts:
                    try:
                        await oauth_service.refresh_tokens(account, db)
                        refreshed_count += 1
                        logger.info(f"Refreshed tokens for account {account.id} ({account.broker})")
                    except Exception as e:
                        logger.error(f"Error refreshing tokens for account {account.id}: {e}")
                        error_count += 1

                logger.info(f"Refreshed {refreshed_count} broker tokens ({error_count} errors)")
                return {"refreshed": refreshed_count, "errors": error_count}

            except Exception as e:
                logger.error(f"Error in refresh_broker_tokens_task: {e}", exc_info=True)
                await db.rollback()
                raise

    return asyncio.run(_refresh())


# ============================================================================
# TRADE MONITORING
# ============================================================================


@celery_app.task(name="monitor_executed_trades")
def monitor_executed_trades_task():
    """
    Monitor pending executed trades and update their status.

    Runs every 2 minutes to check order fill status.
    """
    import asyncio

    async def _monitor():
        async with db_manager.get_session() as db:
            try:
                # Get pending trades from last 24 hours
                since = datetime.utcnow() - timedelta(hours=24)
                stmt = select(ExecutedTrade).where(
                    and_(
                        ExecutedTrade.execution_status == "pending",
                        ExecutedTrade.created_at >= since,
                    )
                )
                result = await db.execute(stmt)
                pending_trades = result.scalars().all()

                updated_count = 0
                error_count = 0

                for trade in pending_trades:
                    try:
                        # Get account
                        account = await db.get(BrokerageAccount, trade.brokerage_account_id)
                        if not account or not account.is_active:
                            continue

                        # Get broker client
                        from app.services.broker_clients import get_broker_client

                        access_token = oauth_service.encryption.decrypt(account.access_token)
                        broker_client = get_broker_client(account.broker, access_token)

                        # Get order status
                        if trade.broker_order_id:
                            order_status = await broker_client.get_order_status(trade.broker_order_id)

                            # Update trade
                            trade.execution_status = order_status["status"]
                            if order_status["filled_quantity"]:
                                trade.shares = order_status["filled_quantity"]
                            if order_status["filled_price"]:
                                trade.price = order_status["filled_price"]
                            if order_status["status"] == "filled":
                                trade.filled_at = datetime.utcnow()

                            updated_count += 1

                    except Exception as e:
                        logger.error(f"Error monitoring trade {trade.id}: {e}")
                        error_count += 1

                await db.commit()

                logger.info(f"Monitored {len(pending_trades)} pending trades ({updated_count} updated, {error_count} errors)")
                return {"monitored": len(pending_trades), "updated": updated_count, "errors": error_count}

            except Exception as e:
                logger.error(f"Error in monitor_executed_trades_task: {e}", exc_info=True)
                await db.rollback()
                raise

    return asyncio.run(_monitor())
