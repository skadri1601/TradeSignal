"""
Brokerage API Router

Endpoints for brokerage account connections, copy trading rules, and trade execution.
Supports Alpaca, TD Ameritrade, and Interactive Brokers.
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.middleware.feature_gating import require_tier
from app.models.user import User
from app.models.brokerage import BrokerageAccount, CopyTradeRule, ExecutedTrade
from app.schemas.brokerage import (
    BrokerageAccountResponse,
    CopyTradeRuleCreate,
    CopyTradeRuleUpdate,
    CopyTradeRuleResponse,
    ExecutedTradeResponse,
    OAuthAuthorizationResponse,
    OAuthCallbackResponse,
    BrokerAccountSummary,
    BrokerPositionResponse,
    BrokerOrderResponse,
    ManualTradeRequest,
)
from app.services.oauth_service import oauth_service
from app.services.brokerage_service import BrokerageService
from app.services.broker_clients import get_broker_client

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
ERROR_BROKERAGE_NOT_FOUND = "Brokerage account not found"
ERROR_COPY_RULE_NOT_FOUND = "Copy trade rule not found"


# ============================================================================
# OAUTH ENDPOINTS
# ============================================================================


@router.get("/connect/{broker}", response_model=OAuthAuthorizationResponse)
async def initiate_broker_connection(
    broker: str,
    current_user: User = Depends(require_tier("plus", "Copy Trading")),
    redirect_uri: Optional[str] = None,
):
    """
    Initiate OAuth connection to a broker.

    Returns authorization URL for user to complete OAuth flow.
    Supports: alpaca, td_ameritrade, interactive_brokers
    """
    try:
        if broker == "alpaca":
            result = oauth_service.get_alpaca_auth_url(current_user.id, redirect_uri)
        elif broker == "td_ameritrade":
            result = oauth_service.get_td_ameritrade_auth_url(current_user.id, redirect_uri)
        elif broker == "interactive_brokers":
            result = oauth_service.get_interactive_brokers_auth_url(current_user.id, redirect_uri)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported broker: {broker}",
            )

        return OAuthAuthorizationResponse(**result)
    except Exception as e:
        logger.error(f"Error initiating broker connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate broker connection: {str(e)}",
        )


@router.get("/callback/{broker}", response_model=OAuthCallbackResponse)
async def handle_broker_callback(
    broker: str,
    code: str,
    state: str,
    redirect_uri: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from broker.

    This endpoint is called by the broker after user authorizes the connection.
    Creates brokerage account and stores encrypted tokens.
    """
    try:
        if broker == "alpaca":
            account = await oauth_service.handle_alpaca_callback(code, state, db, redirect_uri)
        elif broker == "td_ameritrade":
            account = await oauth_service.handle_td_ameritrade_callback(code, state, db, redirect_uri)
        elif broker == "interactive_brokers":
            account = await oauth_service.handle_interactive_brokers_callback(code, state, db, redirect_uri)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported broker: {broker}",
            )

        return OAuthCallbackResponse(
            success=True,
            account_id=account.id,
            broker=account.broker,
            account_number=account.account_number,
            message=f"Successfully connected to {broker}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error handling broker callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect broker account: {str(e)}",
        )


@router.post("/disconnect")
async def disconnect_broker(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect a brokerage account.

    Revokes OAuth tokens and deactivates the account.
    """
    try:
        # Get account
        account = await db.get(BrokerageAccount, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_BROKERAGE_NOT_FOUND,
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to disconnect this account",
            )

        # Revoke tokens
        await oauth_service.revoke_tokens(account, db)

        return {"success": True, "message": "Account disconnected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting broker: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect account: {str(e)}",
        )


# ============================================================================
# ACCOUNT ENDPOINTS
# ============================================================================


@router.get("/accounts", response_model=List[BrokerageAccountResponse])
async def get_brokerage_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all brokerage accounts for the current user."""
    service = BrokerageService(db)
    accounts = await service.get_user_brokerage_accounts(current_user.id)
    return accounts


@router.get("/accounts/{account_id}", response_model=BrokerAccountSummary)
async def get_account_details(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed account information including positions and recent orders.
    """
    try:
        # Get account
        account = await db.get(BrokerageAccount, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_BROKERAGE_NOT_FOUND,
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this account",
            )

        # Get broker client
        access_token = oauth_service.encryption.decrypt(account.access_token)
        broker_client = get_broker_client(account.broker, access_token)

        # Fetch data in parallel
        account_info = await broker_client.get_account_info()
        positions = await broker_client.get_positions()
        recent_orders = await broker_client.get_recent_orders(limit=10)

        # Calculate totals
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_unrealized_pl = sum(pos["unrealized_pl"] for pos in positions)

        return BrokerAccountSummary(
            account=BrokerageAccountResponse.model_validate(account),
            positions=[BrokerPositionResponse(**pos) for pos in positions],
            recent_orders=[BrokerOrderResponse(**order) for order in recent_orders],
            total_positions=len(positions),
            total_market_value=total_market_value,
            total_unrealized_pl=total_unrealized_pl,
            cash_balance=account_info["balance"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch account details: {str(e)}",
        )


@router.post("/accounts/{account_id}/sync")
async def sync_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually sync account data from broker API.

    Updates balance, buying power, and portfolio value.
    """
    try:
        # Get account
        account = await db.get(BrokerageAccount, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_BROKERAGE_NOT_FOUND,
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to sync this account",
            )

        # Fetch account info
        service = BrokerageService(db)
        account_info = await service._fetch_account_info(account)

        if account_info:
            account.balance = account_info["balance"]
            account.buying_power = account_info["buying_power"]
            account.portfolio_value = account_info["portfolio_value"]
            account.last_synced_at = datetime.now(timezone.utc)
            await db.commit()

        return {"success": True, "message": "Account synced successfully", "account": account}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync account: {str(e)}",
        )


# ============================================================================
# COPY TRADE RULES ENDPOINTS
# ============================================================================


@router.get("/rules", response_model=List[CopyTradeRuleResponse])
async def get_copy_trade_rules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all copy trade rules for the current user."""
    service = BrokerageService(db)
    rules = await service.get_copy_trade_rules(current_user.id)

    # Enhance with account names
    result = []
    for rule in rules:
        account = await db.get(BrokerageAccount, rule.brokerage_account_id)
        rule_dict = {
            "id": rule.id,
            "user_id": rule.user_id,
            "name": rule.rule_name,
            "description": None,
            "brokerage_account_id": rule.brokerage_account_id,
            "brokerage_account_name": account.account_name if account else None,
            "is_active": rule.is_active,
            "conditions": rule.source_filter or {},
            "copy_percentage": rule.position_size_value,
            "max_position_size": rule.max_position_size,
            "order_type": "market",
            "time_in_force": "day",
            "trades_executed": rule.total_trades_executed or 0,
            "total_volume": 0,
            "last_executed_at": None,
            "created_at": rule.created_at,
            "updated_at": rule.updated_at,
        }
        result.append(CopyTradeRuleResponse(**rule_dict))

    return result


@router.post("/rules", response_model=CopyTradeRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_copy_trade_rule(
    rule_data: CopyTradeRuleCreate,
    current_user: User = Depends(require_tier("plus", "Copy Trading Rules")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new copy trade rule."""
    try:
        service = BrokerageService(db)

        # Convert conditions to source_filter format
        source_filter = {
            "conditions": [cond.model_dump() for cond in rule_data.conditions]
        }

        rule = await service.create_copy_trade_rule(
            user_id=current_user.id,
            brokerage_account_id=rule_data.brokerage_account_id,
            rule_name=rule_data.name,
            source_type="insider_trades",
            source_filter=source_filter,
            position_size_type="percentage",
            position_size_value=float(rule_data.copy_percentage),
            max_position_size=float(rule_data.max_position_size) if rule_data.max_position_size else None,
        )

        # Get account name
        account = await db.get(BrokerageAccount, rule.brokerage_account_id)

        return CopyTradeRuleResponse(
            id=rule.id,
            user_id=rule.user_id,
            name=rule.rule_name,
            description=None,
            brokerage_account_id=rule.brokerage_account_id,
            brokerage_account_name=account.account_name if account else None,
            is_active=rule.is_active,
            conditions=rule.source_filter or {},
            copy_percentage=rule.position_size_value,
            max_position_size=rule.max_position_size,
            order_type="market",
            time_in_force="day",
            trades_executed=rule.total_trades_executed or 0,
            total_volume=0,
            last_executed_at=None,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating copy trade rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}",
        )


@router.put("/rules/{rule_id}", response_model=CopyTradeRuleResponse)
async def update_copy_trade_rule(
    rule_id: int,
    rule_data: CopyTradeRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing copy trade rule."""
    try:
        # Get rule
        rule = await db.get(CopyTradeRule, rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COPY_RULE_NOT_FOUND,
            )

        # Verify ownership
        if rule.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this rule",
            )

        # Update fields
        if rule_data.name:
            rule.rule_name = rule_data.name
        if rule_data.is_active is not None:
            rule.is_active = rule_data.is_active
        if rule_data.conditions:
            rule.source_filter = {"conditions": [cond.model_dump() for cond in rule_data.conditions]}
        if rule_data.copy_percentage:
            rule.position_size_value = float(rule_data.copy_percentage)
        if rule_data.max_position_size:
            rule.max_position_size = float(rule_data.max_position_size)

        await db.commit()
        await db.refresh(rule)

        # Get account name
        account = await db.get(BrokerageAccount, rule.brokerage_account_id)

        return CopyTradeRuleResponse(
            id=rule.id,
            user_id=rule.user_id,
            name=rule.rule_name,
            description=None,
            brokerage_account_id=rule.brokerage_account_id,
            brokerage_account_name=account.account_name if account else None,
            is_active=rule.is_active,
            conditions=rule.source_filter or {},
            copy_percentage=rule.position_size_value,
            max_position_size=rule.max_position_size,
            order_type="market",
            time_in_force="day",
            trades_executed=rule.total_trades_executed or 0,
            total_volume=0,
            last_executed_at=None,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating copy trade rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}",
        )


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_copy_trade_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a copy trade rule."""
    try:
        # Get rule
        rule = await db.get(CopyTradeRule, rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COPY_RULE_NOT_FOUND,
            )

        # Verify ownership
        if rule.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this rule",
            )

        await db.delete(rule)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting copy trade rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rule: {str(e)}",
        )


@router.post("/rules/{rule_id}/toggle")
async def toggle_rule_status(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a copy trade rule active/inactive status."""
    try:
        # Get rule
        rule = await db.get(CopyTradeRule, rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COPY_RULE_NOT_FOUND,
            )

        # Verify ownership
        if rule.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this rule",
            )

        # Toggle status
        rule.is_active = not rule.is_active
        await db.commit()

        return {
            "success": True,
            "is_active": rule.is_active,
            "message": f"Rule {'activated' if rule.is_active else 'deactivated'} successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling rule status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle rule status: {str(e)}",
        )


# ============================================================================
# EXECUTED TRADES ENDPOINTS
# ============================================================================


@router.get("/trades", response_model=List[ExecutedTradeResponse])
async def get_executed_trades(
    current_user: User = Depends(get_current_user),
    rule_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get executed trades for the current user."""
    try:
        from sqlalchemy import select, desc

        # Build query
        query = select(ExecutedTrade).join(CopyTradeRule).where(
            CopyTradeRule.user_id == current_user.id
        )

        if rule_id:
            query = query.where(ExecutedTrade.copy_trade_rule_id == rule_id)

        query = query.order_by(desc(ExecutedTrade.created_at)).limit(limit).offset(offset)

        result = await db.execute(query)
        trades = result.scalars().all()

        # Enhance with rule names
        response_trades = []
        for trade in trades:
            rule = await db.get(CopyTradeRule, trade.copy_trade_rule_id)
            response_trades.append(
                ExecutedTradeResponse(
                    id=trade.id,
                    rule_id=trade.copy_trade_rule_id,
                    rule_name=rule.rule_name if rule else "Unknown",
                    user_id=current_user.id,
                    brokerage_account_id=trade.brokerage_account_id,
                    insider_trade_id=trade.source_trade_id or 0,
                    ticker=trade.ticker,
                    side=trade.transaction_type,
                    quantity=trade.shares,
                    order_type="market",
                    limit_price=None,
                    stop_price=None,
                    filled_quantity=trade.shares if trade.execution_status == "filled" else 0,
                    filled_price=trade.price,
                    status=trade.execution_status,
                    broker_order_id=trade.broker_order_id,
                    execution_time=trade.filled_at,
                    error_message=None,
                    created_at=trade.created_at,
                )
            )

        return response_trades
    except Exception as e:
        logger.error(f"Error fetching executed trades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trades: {str(e)}",
        )


@router.get("/trades/{trade_id}", response_model=ExecutedTradeResponse)
async def get_trade_details(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific executed trade."""
    try:
        trade = await db.get(ExecutedTrade, trade_id)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found",
            )

        # Verify ownership through rule
        rule = await db.get(CopyTradeRule, trade.copy_trade_rule_id)
        if not rule or rule.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this trade",
            )

        return ExecutedTradeResponse(
            id=trade.id,
            rule_id=trade.copy_trade_rule_id,
            rule_name=rule.rule_name,
            user_id=current_user.id,
            brokerage_account_id=trade.brokerage_account_id,
            insider_trade_id=trade.source_trade_id or 0,
            ticker=trade.ticker,
            side=trade.transaction_type,
            quantity=trade.shares,
            order_type="market",
            limit_price=None,
            stop_price=None,
            filled_quantity=trade.shares if trade.execution_status == "filled" else 0,
            filled_price=trade.price,
            status=trade.execution_status,
            broker_order_id=trade.broker_order_id,
            execution_time=trade.filled_at,
            error_message=None,
            created_at=trade.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trade details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trade details: {str(e)}",
        )


# ============================================================================
# MANUAL TRADING ENDPOINT
# ============================================================================


@router.post("/manual-trade", response_model=ExecutedTradeResponse, status_code=status.HTTP_201_CREATED)
async def place_manual_trade(
    trade_request: ManualTradeRequest,
    current_user: User = Depends(require_tier("plus", "Manual Trading")),
    db: AsyncSession = Depends(get_db),
):
    """
    Place a manual trade through connected broker.

    Bypasses copy trade rules for manual execution.
    """
    try:
        # Get account
        account = await db.get(BrokerageAccount, trade_request.brokerage_account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_BROKERAGE_NOT_FOUND,
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to trade with this account",
            )

        # Get broker client
        access_token = oauth_service.encryption.decrypt(account.access_token)
        broker_client = get_broker_client(account.broker, access_token)

        # Place order
        order_result = await broker_client.place_order(
            ticker=trade_request.ticker,
            side=trade_request.side,
            quantity=trade_request.quantity,
            order_type=trade_request.order_type,
            limit_price=trade_request.limit_price,
            stop_price=trade_request.stop_price,
            time_in_force=trade_request.time_in_force,
        )

        # Create executed trade record (without rule)
        executed_trade = ExecutedTrade(
            copy_trade_rule_id=None,
            brokerage_account_id=account.id,
            ticker=trade_request.ticker.upper(),
            transaction_type=trade_request.side,
            shares=trade_request.quantity,
            price=order_result.get("filled_price"),
            total_value=float(trade_request.quantity) * float(order_result.get("filled_price", 0)),
            execution_status=order_result.get("status", "pending"),
            broker_order_id=order_result.get("broker_order_id"),
            filled_at=order_result.get("created_at"),
        )
        db.add(executed_trade)
        await db.commit()
        await db.refresh(executed_trade)

        return ExecutedTradeResponse(
            id=executed_trade.id,
            rule_id=0,
            rule_name="Manual Trade",
            user_id=current_user.id,
            brokerage_account_id=account.id,
            insider_trade_id=0,
            ticker=executed_trade.ticker,
            side=executed_trade.transaction_type,
            quantity=executed_trade.shares,
            order_type=trade_request.order_type,
            limit_price=trade_request.limit_price,
            stop_price=trade_request.stop_price,
            filled_quantity=order_result.get("filled_quantity", 0),
            filled_price=order_result.get("filled_price"),
            status=executed_trade.execution_status,
            broker_order_id=executed_trade.broker_order_id,
            execution_time=executed_trade.filled_at,
            error_message=None,
            created_at=executed_trade.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error placing manual trade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place trade: {str(e)}",
        )
