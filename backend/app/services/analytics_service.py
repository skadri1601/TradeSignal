"""
Analytics Service.

Event tracking, funnel analysis, executive dashboard, data warehouse ETL.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.analytics import (
    AnalyticsEvent,
    FunnelStep,
    FunnelAnalysis,
    ExecutiveDashboard,
    DataWarehouseETL,
)
from app.models.user import User
from app.models.subscription import Subscription

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and metrics tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def track_event(
        self,
        event_name: str,
        event_category: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        event_properties: Optional[Dict[str, Any]] = None,
        page_path: Optional[str] = None,
        referrer: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AnalyticsEvent:
        """Track an analytics event."""
        event = AnalyticsEvent(
            user_id=user_id,
            session_id=session_id,
            event_name=event_name,
            event_category=event_category,
            event_properties=event_properties,
            page_path=page_path,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def analyze_funnel(
        self,
        funnel_name: str,
        period_start: datetime,
        period_end: datetime,
    ) -> FunnelAnalysis:
        """
        Analyze a conversion funnel.

        Calculates step conversions and drop-off rates.
        """
        # Get funnel steps
        result = await self.db.execute(
            select(FunnelStep)
            .where(FunnelStep.funnel_name == funnel_name)
            .order_by(FunnelStep.step_order)
        )
        steps = result.scalars().all()

        if not steps:
            raise ValueError(f"Funnel {funnel_name} not found")

        # Get unique users who reached first step
        first_step = steps[0]
        first_step_users = await self.db.execute(
            select(func.count(func.distinct(AnalyticsEvent.user_id)))
            .where(
                AnalyticsEvent.event_name == first_step.event_name,
                AnalyticsEvent.created_at >= period_start,
                AnalyticsEvent.created_at <= period_end,
            )
        )
        total_users = first_step_users.scalar() or 0

        # Calculate conversions for each step
        step_conversions = {}
        conversion_rates = {}
        previous_count = total_users

        for step in steps:
            step_users = await self.db.execute(
                select(func.count(func.distinct(AnalyticsEvent.user_id)))
                .where(
                    AnalyticsEvent.event_name == step.event_name,
                    AnalyticsEvent.created_at >= period_start,
                    AnalyticsEvent.created_at <= period_end,
                )
            )
            step_count = step_users.scalar() or 0

            step_conversions[step.step_name] = step_count
            conversion_rate = (
                (step_count / previous_count * 100) if previous_count > 0 else 0
            )
            conversion_rates[step.step_name] = round(conversion_rate, 2)

            previous_count = step_count

        # Identify drop-off points
        drop_off_points = {}
        for i, step in enumerate(steps[:-1]):
            current_count = step_conversions.get(step.step_name, 0)
            next_count = step_conversions.get(steps[i + 1].step_name, 0)
            drop_off = current_count - next_count
            if drop_off > 0:
                drop_off_points[step.step_name] = drop_off

        # Create analysis record
        analysis = FunnelAnalysis(
            funnel_name=funnel_name,
            period_start=period_start,
            period_end=period_end,
            total_users=total_users,
            step_conversions=step_conversions,
            conversion_rates=conversion_rates,
            drop_off_points=drop_off_points,
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        return analysis

    async def generate_executive_dashboard(
        self, report_date: datetime, period_type: str = "daily"
    ) -> ExecutiveDashboard:
        """
        Generate executive dashboard metrics.

        Aggregates key business metrics for reporting.
        """
        # Calculate period boundaries
        if period_type == "daily":
            period_start = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period_type == "weekly":
            period_start = report_date - timedelta(days=report_date.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7)
        elif period_type == "monthly":
            period_start = report_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        else:
            raise ValueError(f"Invalid period_type: {period_type}")

        # User metrics
        total_users_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0

        active_users_result = await self.db.execute(
            select(func.count(func.distinct(AnalyticsEvent.user_id)))
            .where(
                AnalyticsEvent.created_at >= period_start,
                AnalyticsEvent.created_at < period_end,
            )
        )
        active_users = active_users_result.scalar() or 0

        new_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(
                User.created_at >= period_start,
                User.created_at < period_end,
            )
        )
        new_users = new_users_result.scalar() or 0

        # Revenue metrics
        subscriptions_result = await self.db.execute(
            select(
                func.sum(Subscription.amount).label("total_revenue"),
                func.sum(
                    func.case(
                        (Subscription.billing_period == "monthly", Subscription.amount),
                        else_=Subscription.amount / 12,
                    )
                ).label("mrr"),
            )
            .where(
                Subscription.status == "active",
            )
        )
        revenue_stats = subscriptions_result.first()
        total_revenue = float(revenue_stats.total_revenue or 0)
        mrr = float(revenue_stats.mrr or 0)
        arr = mrr * 12

        # Engagement metrics
        trades_viewed_result = await self.db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.event_name == "trade_viewed",
                AnalyticsEvent.created_at >= period_start,
                AnalyticsEvent.created_at < period_end,
            )
        )
        total_trades_viewed = trades_viewed_result.scalar() or 0

        alerts_created_result = await self.db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.event_name == "alert_created",
                AnalyticsEvent.created_at >= period_start,
                AnalyticsEvent.created_at < period_end,
            )
        )
        total_alerts_created = alerts_created_result.scalar() or 0

        api_calls_result = await self.db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.event_category == "api",
                AnalyticsEvent.created_at >= period_start,
                AnalyticsEvent.created_at < period_end,
            )
        )
        total_api_calls = api_calls_result.scalar() or 0

        # Conversion metrics
        free_users_result = await self.db.execute(
            select(func.count(User.id))
            .join(Subscription, User.id == Subscription.user_id, isouter=True)
            .where(Subscription.id.is_(None))
        )
        free_users = free_users_result.scalar() or 0

        paid_users_result = await self.db.execute(
            select(func.count(func.distinct(Subscription.user_id)))
            .where(Subscription.status == "active")
        )
        paid_users = paid_users_result.scalar() or 0

        conversion_rate = (
            (paid_users / (free_users + paid_users) * 100) if (free_users + paid_users) > 0 else 0
        )

        # Create dashboard record
        dashboard = ExecutiveDashboard(
            report_date=report_date,
            period_type=period_type,
            total_users=total_users,
            active_users=active_users,
            new_users=new_users,
            churned_users=0,  # Would calculate from cancellation events
            total_revenue=total_revenue,
            mrr=mrr,
            arr=arr,
            total_trades_viewed=total_trades_viewed,
            total_alerts_created=total_alerts_created,
            total_api_calls=total_api_calls,
            free_to_paid_conversion_rate=round(conversion_rate, 2),
        )
        self.db.add(dashboard)
        await self.db.commit()
        await self.db.refresh(dashboard)

        return dashboard

    async def run_etl_job(
        self, job_name: str, source_table: str, target_table: str
    ) -> DataWarehouseETL:
        """
        Run ETL job for data warehouse.

        Tracks ETL pipeline execution.
        """
        etl_job = DataWarehouseETL(
            job_name=job_name,
            source_table=source_table,
            target_table=target_table,
            status="running",
            started_at=datetime.utcnow(),
        )
        self.db.add(etl_job)
        await self.db.flush()

        try:
            # ETL logic would go here
            # For now, simulate processing
            records_processed = 0
            records_failed = 0

            # Update job status
            etl_job.status = "completed"
            etl_job.completed_at = datetime.utcnow()
            etl_job.records_processed = records_processed
            etl_job.records_failed = records_failed
            etl_job.duration_seconds = (
                (etl_job.completed_at - etl_job.started_at).total_seconds()
            )

            await self.db.commit()
            await self.db.refresh(etl_job)

            return etl_job

        except Exception as e:
            etl_job.status = "failed"
            etl_job.completed_at = datetime.utcnow()
            etl_job.error_message = str(e)
            etl_job.duration_seconds = (
                (etl_job.completed_at - etl_job.started_at).total_seconds()
            )

            await self.db.commit()
            await self.db.refresh(etl_job)

            raise

