"""
Brokerage Integration models.

Copy trading infrastructure, OAuth with broker APIs, account linking, trade execution.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Index, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BrokerageAccount(Base):
    """
    Brokerage account model.

    Links user accounts to brokerage platforms.
    """

    __tablename__ = "brokerage_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Brokerage details
    brokerage_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., "alpaca", "td_ameritrade"
    account_id: Mapped[str] = mapped_column(String(100), nullable=False)  # Broker's account ID
    account_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # OAuth tokens (encrypted in production)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Account balance (cached)
    account_balance: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    buying_power: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # Timestamps
    connected_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<BrokerageAccount(id={self.id}, brokerage={self.brokerage_name}, user_id={self.user_id})>"


class CopyTradeRule(Base):
    """
    Copy trading rule model.

    Defines rules for automatically copying trades.
    """

    __tablename__ = "copy_trade_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brokerage_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("brokerage_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Rule configuration
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "politician", "insider", "signal"
    source_filter: Mapped[str] = mapped_column(JSON, nullable=True)  # Filter criteria

    # Trade execution settings
    position_size_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="percentage"
    )  # "percentage", "fixed_dollar", "shares"
    position_size_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Size value
    max_position_size: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)  # Max $ per trade

    # Risk management
    max_daily_trades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_daily_loss: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    stop_loss_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    take_profit_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Statistics
    total_trades_executed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_profit_loss: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<CopyTradeRule(id={self.id}, rule_name={self.rule_name}, user_id={self.user_id})>"


class ExecutedTrade(Base):
    """
    Executed trade model.

    Tracks trades executed through copy trading.
    """

    __tablename__ = "executed_trades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    copy_trade_rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("copy_trade_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brokerage_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("brokerage_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Trade details
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY, SELL
    shares: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Execution details
    broker_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    execution_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, filled, rejected, cancelled
    filled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Source trade reference
    source_trade_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("trades.id", ondelete="SET NULL"), nullable=True
    )
    source_politician_trade_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("congressional_trades.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_executed_trades_rule_created", "copy_trade_rule_id", "created_at"),
        Index("ix_executed_trades_account_created", "brokerage_account_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<ExecutedTrade(id={self.id}, ticker={self.ticker}, "
            f"type={self.transaction_type}, status={self.execution_status})>"
        )

