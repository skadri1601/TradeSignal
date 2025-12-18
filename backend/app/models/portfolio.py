"""
Portfolio Analysis models.

Virtual portfolio creation, position sizing, risk assessment, performance attribution.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Numeric, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VirtualPortfolio(Base):
    """
    Virtual portfolio model.

    User-created portfolios for tracking and analysis.
    """

    __tablename__ = "virtual_portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Portfolio details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Performance metrics (calculated)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    total_return: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    total_return_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)

    # Risk metrics
    portfolio_risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    diversification_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_calculated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    positions: Mapped[list["PortfolioPosition"]] = relationship(
        "PortfolioPosition", back_populates="portfolio", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<VirtualPortfolio(id={self.id}, name={self.name}, user_id={self.user_id})>"


class PortfolioPosition(Base):
    """
    Portfolio position model.

    Individual stock positions within a virtual portfolio.
    """

    __tablename__ = "portfolio_positions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Position details
    shares: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    average_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Average purchase price
    current_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Calculated metrics
    cost_basis: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)  # shares * average_cost
    current_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)  # shares * current_price
    unrealized_gain_loss: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    unrealized_gain_loss_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Position sizing
    position_size_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False
    )  # % of portfolio

    # Risk metrics
    position_risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    portfolio: Mapped["VirtualPortfolio"] = relationship(
        "VirtualPortfolio", back_populates="positions"
    )

    __table_args__ = (
        Index("ix_portfolio_positions_portfolio_ticker", "portfolio_id", "ticker", unique=True),
    )

    def __repr__(self) -> str:
        return f"<PortfolioPosition(id={self.id}, ticker={self.ticker}, shares={self.shares})>"


class PortfolioTransaction(Base):
    """
    Portfolio transaction history.

    Tracks buy/sell transactions for performance attribution.
    """

    __tablename__ = "portfolio_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("portfolio_positions.id", ondelete="SET NULL"), nullable=True
    )

    # Transaction details
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY, SELL
    shares: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Transaction date
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_portfolio_transactions_portfolio_date", "portfolio_id", "transaction_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<PortfolioTransaction(id={self.id}, ticker={self.ticker}, "
            f"type={self.transaction_type}, shares={self.shares})>"
        )


class PortfolioPerformance(Base):
    """
    Portfolio performance snapshot.

    Historical performance tracking for attribution analysis.
    """

    __tablename__ = "portfolio_performance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Snapshot date
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Performance metrics
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_return: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_return_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Period returns
    daily_return: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    weekly_return: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    monthly_return: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ytd_return: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Risk metrics
    portfolio_risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    sharpe_ratio: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_portfolio_performance_portfolio_date", "portfolio_id", "snapshot_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<PortfolioPerformance(id={self.id}, portfolio_id={self.portfolio_id}, "
            f"date={self.snapshot_date}, return={self.total_return_pct}%)>"
        )

