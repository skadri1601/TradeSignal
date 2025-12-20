"""
Pydantic schemas for Brokerage and Copy Trading API.
"""

from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS AND LITERALS
# ============================================================================

BrokerType = Literal["alpaca", "td_ameritrade", "interactive_brokers"]
OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "stop", "stop_limit"]
TimeInForce = Literal["day", "gtc", "ioc", "fok"]
RuleConditionField = Literal[
    "transaction_type",
    "security_type",
    "share_volume",
    "transaction_value",
    "ticker",
    "insider_title",
    "company_sector",
]
RuleConditionOperator = Literal["equals", "not_equals", "greater_than", "less_than", "contains", "in"]


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================


class BrokerageConnectionRequest(BaseModel):
    """Schema for initiating brokerage connection (OAuth flow)."""

    broker: BrokerType
    redirect_uri: Optional[str] = Field(None, description="Custom redirect URI for OAuth callback")


class BrokerageDisconnectRequest(BaseModel):
    """Schema for disconnecting a brokerage account."""

    account_id: int = Field(..., gt=0)


class RuleCondition(BaseModel):
    """Schema for a single copy trade rule condition."""

    field: RuleConditionField
    operator: RuleConditionOperator
    value: Any = Field(..., description="Value to compare against (type depends on field)")


class CopyTradeRuleCreate(BaseModel):
    """Schema for creating a new copy trade rule."""

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    brokerage_account_id: int = Field(..., gt=0)
    is_active: bool = True
    conditions: List[RuleCondition] = Field(..., min_items=1, max_items=10)
    copy_percentage: Decimal = Field(..., ge=0.01, le=100, description="Percentage of position to copy (1-100)")
    max_position_size: Optional[Decimal] = Field(None, ge=0, description="Maximum dollar amount per position")
    order_type: OrderType = Field(default="market")
    time_in_force: TimeInForce = Field(default="day")


class CopyTradeRuleUpdate(BaseModel):
    """Schema for updating an existing copy trade rule."""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    conditions: Optional[List[RuleCondition]] = Field(None, min_items=1, max_items=10)
    copy_percentage: Optional[Decimal] = Field(None, ge=0.01, le=100)
    max_position_size: Optional[Decimal] = Field(None, ge=0)
    order_type: Optional[OrderType] = None
    time_in_force: Optional[TimeInForce] = None


class ManualTradeRequest(BaseModel):
    """Schema for placing a manual trade through connected broker."""

    brokerage_account_id: int = Field(..., gt=0)
    ticker: str = Field(..., min_length=1, max_length=10)
    side: OrderSide
    quantity: Decimal = Field(..., gt=0)
    order_type: OrderType = Field(default="market")
    limit_price: Optional[Decimal] = Field(None, gt=0)
    stop_price: Optional[Decimal] = Field(None, gt=0)
    time_in_force: TimeInForce = Field(default="day")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class BrokerageAccountResponse(BaseModel):
    """Schema for brokerage account response."""

    id: int
    user_id: int
    broker: str
    account_number: str
    account_name: Optional[str]
    is_active: bool
    balance: Optional[Decimal]
    buying_power: Optional[Decimal]
    portfolio_value: Optional[Decimal]
    last_synced_at: Optional[datetime]
    connected_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CopyTradeRuleResponse(BaseModel):
    """Schema for copy trade rule response."""

    id: int
    user_id: int
    name: str
    description: Optional[str]
    brokerage_account_id: int
    brokerage_account_name: Optional[str]
    is_active: bool
    conditions: List[Dict[str, Any]]  # JSON conditions
    copy_percentage: Decimal
    max_position_size: Optional[Decimal]
    order_type: str
    time_in_force: str
    trades_executed: int
    total_volume: Decimal
    last_executed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExecutedTradeResponse(BaseModel):
    """Schema for executed trade response."""

    id: int
    rule_id: int
    rule_name: str
    user_id: int
    brokerage_account_id: int
    insider_trade_id: int
    ticker: str
    side: str
    quantity: Decimal
    order_type: str
    limit_price: Optional[Decimal]
    stop_price: Optional[Decimal]
    filled_quantity: Optional[Decimal]
    filled_price: Optional[Decimal]
    status: str  # pending, filled, partial, cancelled, failed
    broker_order_id: Optional[str]
    execution_time: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OAuthAuthorizationResponse(BaseModel):
    """Schema for OAuth authorization URL response."""

    authorization_url: str
    state: str = Field(..., description="CSRF state token to validate callback")


class OAuthCallbackResponse(BaseModel):
    """Schema for OAuth callback success response."""

    success: bool
    account_id: int
    broker: str
    account_number: str
    message: str


class BrokerPositionResponse(BaseModel):
    """Schema for broker position response."""

    ticker: str
    quantity: Decimal
    market_value: Decimal
    cost_basis: Decimal
    unrealized_pl: Decimal
    unrealized_pl_pct: Decimal
    current_price: Decimal


class BrokerOrderResponse(BaseModel):
    """Schema for broker order response."""

    broker_order_id: str
    ticker: str
    side: str
    quantity: Decimal
    order_type: str
    status: str
    filled_quantity: Optional[Decimal]
    filled_price: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]


class RuleExecutionStats(BaseModel):
    """Schema for rule execution statistics."""

    rule_id: int
    rule_name: str
    total_trades: int
    successful_trades: int
    failed_trades: int
    total_volume: Decimal
    avg_fill_price: Optional[Decimal]
    win_rate: Optional[Decimal]
    total_pnl: Optional[Decimal]
    last_executed_at: Optional[datetime]


class BrokerAccountSummary(BaseModel):
    """Schema for broker account summary with positions and stats."""

    account: BrokerageAccountResponse
    positions: List[BrokerPositionResponse]
    recent_orders: List[BrokerOrderResponse]
    total_positions: int
    total_market_value: Decimal
    total_unrealized_pl: Decimal
    cash_balance: Decimal
