"""
Market Data Models

Stores cached market data from yfinance and Finnhub.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DividendHistory(Base):
    """Historical dividend payments for a company."""
    __tablename__ = "dividend_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    ex_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_dividend_company_date", "company_id", "ex_date"),
    )


class EarningsCalendar(Base):
    """Upcoming and past earnings dates."""
    __tablename__ = "earnings_calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    earnings_date: Mapped[date] = mapped_column(Date, nullable=False)
    earnings_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'BMO', 'AMC', 'TAS'
    eps_estimate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    eps_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    revenue_estimate: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    revenue_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_earnings_company_date", "company_id", "earnings_date"),
    )


class AnalystRecommendation(Base):
    """Analyst recommendations (Buy/Hold/Sell)."""
    __tablename__ = "analyst_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    period: Mapped[date] = mapped_column(Date, nullable=False)  # Month of recommendation
    strong_buy: Mapped[int] = mapped_column(Integer, default=0)
    buy: Mapped[int] = mapped_column(Integer, default=0)
    hold: Mapped[int] = mapped_column(Integer, default=0)
    sell: Mapped[int] = mapped_column(Integer, default=0)
    strong_sell: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_analyst_company_period", "company_id", "period"),
    )


class FinancialStatement(Base):
    """Quarterly/Annual financial statements."""
    __tablename__ = "financial_statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'quarterly', 'annual'
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    statement_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'income', 'balance', 'cashflow'
    data: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full statement as JSON
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_financial_company_period", "company_id", "period_end", "statement_type"),
    )


class PriceTarget(Base):
    """Analyst price targets from Finnhub."""
    __tablename__ = "price_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    target_high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    target_low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    target_mean: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    target_median: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    last_updated: Mapped[date] = mapped_column(Date, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_price_target_company", "company_id"),
    )


class EarningsSurprise(Base):
    """Historical earnings surprises (actual vs estimate)."""
    __tablename__ = "earnings_surprises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    period: Mapped[date] = mapped_column(Date, nullable=False)
    actual_eps: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    estimate_eps: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    surprise: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)  # actual - estimate
    surprise_percent: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_surprise_company_period", "company_id", "period"),
    )

