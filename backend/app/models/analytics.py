"""
Analytics & Metrics models.

Event tracking, funnel analysis, executive dashboard, data warehouse ETL pipeline.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Index, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnalyticsEvent(Base):
    """
    Analytics event tracking model.

    Tracks user actions and events for funnel analysis.
    """

    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Event details
    event_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_properties: Mapped[str | None] = mapped_column(JSON, nullable=True)  # Additional event data

    # User context
    page_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_analytics_events_user_created", "user_id", "created_at"),
        Index("ix_analytics_events_category_created", "event_category", "created_at"),
        Index("ix_analytics_events_name_created", "event_name", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AnalyticsEvent(id={self.id}, event_name={self.event_name}, user_id={self.user_id})>"


class FunnelStep(Base):
    """
    Funnel step definition model.

    Defines steps in conversion funnels for analysis.
    """

    __tablename__ = "funnel_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    funnel_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_funnel_steps_funnel_order", "funnel_name", "step_order"),
    )

    def __repr__(self) -> str:
        return f"<FunnelStep(id={self.id}, funnel_name={self.funnel_name}, step_name={self.step_name})>"


class FunnelAnalysis(Base):
    """
    Funnel analysis results model.

    Stores calculated funnel metrics for dashboards.
    """

    __tablename__ = "funnel_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    funnel_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Analysis period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Funnel metrics
    total_users: Mapped[int] = mapped_column(Integer, nullable=False)
    step_conversions: Mapped[str] = mapped_column(JSON, nullable=False)  # {step_name: count}
    conversion_rates: Mapped[str] = mapped_column(JSON, nullable=False)  # {step_name: rate}
    drop_off_points: Mapped[str] = mapped_column(JSON, nullable=True)

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_funnel_analyses_funnel_period", "funnel_name", "period_start"),
    )

    def __repr__(self) -> str:
        return f"<FunnelAnalysis(id={self.id}, funnel_name={self.funnel_name}, period={self.period_start})>"


class ExecutiveDashboard(Base):
    """
    Executive dashboard metrics model.

    Aggregated metrics for executive reporting.
    """

    __tablename__ = "executive_dashboards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Reporting period
    report_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily, weekly, monthly

    # User metrics
    total_users: Mapped[int] = mapped_column(Integer, nullable=False)
    active_users: Mapped[int] = mapped_column(Integer, nullable=False)
    new_users: Mapped[int] = mapped_column(Integer, nullable=False)
    churned_users: Mapped[int] = mapped_column(Integer, nullable=False)

    # Revenue metrics
    total_revenue: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    mrr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)  # Monthly Recurring Revenue
    arr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)  # Annual Recurring Revenue

    # Engagement metrics
    total_trades_viewed: Mapped[int] = mapped_column(Integer, nullable=False)
    total_alerts_created: Mapped[int] = mapped_column(Integer, nullable=False)
    total_api_calls: Mapped[int] = mapped_column(Integer, nullable=False)

    # Conversion metrics
    free_to_paid_conversion_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<ExecutiveDashboard(id={self.id}, report_date={self.report_date}, period={self.period_type})>"


class DataWarehouseETL(Base):
    """
    Data warehouse ETL job tracking model.

    Tracks ETL pipeline runs for data warehouse.
    """

    __tablename__ = "data_warehouse_etl"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    target_table: Mapped[str] = mapped_column(String(100), nullable=False)

    # Job status
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # running, completed, failed
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<DataWarehouseETL(id={self.id}, job_name={self.job_name}, status={self.status})>"

