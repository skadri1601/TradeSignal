"""
Alert Service for TradeSignal.

Handles alert rule matching, trigger detection, and notification coordination.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider
from app.services.notification_service import NotificationService
from app.schemas.alert import AlertCreate, AlertUpdate

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for managing alerts and checking for triggers.

    Responsibilities:
    - CRUD operations for alerts
    - Match trades against active alert rules
    - Trigger notifications when matches found
    - Log alert history
    - Prevent duplicate notifications
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService()

    async def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert."""
        alert = Alert(
            name=alert_data.name,
            alert_type=alert_data.alert_type,
            ticker=alert_data.ticker,
            min_value=alert_data.min_value,
            max_value=alert_data.max_value,
            transaction_type=alert_data.transaction_type,
            insider_roles=alert_data.insider_roles or [],
            notification_channels=alert_data.notification_channels,
            webhook_url=alert_data.webhook_url,
            email=alert_data.email,
            is_active=alert_data.is_active,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"Created alert: {alert.name} (id={alert.id})")
        return alert

    async def get_alert(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID."""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def get_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[list[Alert], int]:
        """Get all alerts with pagination."""
        # Build query
        query = select(Alert)
        if is_active is not None:
            query = query.where(Alert.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        alerts = result.scalars().all()

        return list(alerts), total

    async def update_alert(self, alert_id: int, alert_data: AlertUpdate) -> Optional[Alert]:
        """Update an existing alert."""
        alert = await self.get_alert(alert_id)
        if not alert:
            return None

        # Update fields that were provided
        update_data = alert_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)

        alert.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"Updated alert: {alert.name} (id={alert.id})")
        return alert

    async def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert."""
        alert = await self.get_alert(alert_id)
        if not alert:
            return False

        await self.db.delete(alert)
        await self.db.commit()

        logger.info(f"Deleted alert: {alert.name} (id={alert_id})")
        return True

    async def toggle_alert(self, alert_id: int, is_active: bool) -> Optional[Alert]:
        """Enable or disable an alert."""
        alert = await self.get_alert(alert_id)
        if not alert:
            return None

        alert.is_active = is_active
        alert.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"Toggled alert {alert.name} (id={alert_id}): is_active={is_active}")
        return alert

    async def check_trade_against_alerts(self, trade: Trade) -> None:
        """
        Check a trade against all active alerts and trigger notifications.

        This is called when a new trade is created or updated.
        """
        # Get all active alerts
        alerts, _ = await self.get_alerts(is_active=True, limit=1000)

        if not alerts:
            return

        # Get company and insider info for notifications
        company = await self.db.get(Company, trade.company_id)
        insider = await self.db.get(Insider, trade.insider_id)

        if not company or not insider:
            logger.warning(f"Missing company or insider for trade {trade.id}")
            return

        company_name = company.name
        insider_name = insider.name

        # Check each alert
        for alert in alerts:
            if await self._matches_alert(trade, alert):
                # Check if we already notified for this trade/alert combo (cooldown)
                if await self._recently_notified(alert.id, trade.id):
                    logger.debug(
                        f"Skipping alert {alert.name} for trade {trade.id} (recent notification)"
                    )
                    continue

                # Trigger notifications
                await self._trigger_alert_notifications(
                    alert, trade, company_name, insider_name
                )

    async def _matches_alert(self, trade: Trade, alert: Alert) -> bool:
        """
        Check if a trade matches an alert's criteria.

        Returns True if the trade should trigger this alert.
        """
        # Check ticker filter
        if alert.ticker and alert.ticker.upper() != trade.ticker.upper():
            return False

        # Check transaction type filter
        if alert.transaction_type and alert.transaction_type != trade.transaction_type:
            return False

        # Check value range
        trade_value = float(trade.total_value) if trade.total_value else 0
        if alert.min_value and trade_value < float(alert.min_value):
            return False
        if alert.max_value and trade_value > float(alert.max_value):
            return False

        # Check insider role filter
        if alert.insider_roles:
            # Get insider from DB
            insider = await self.db.get(Insider, trade.insider_id)
            if insider:
                # Check if any of the alert's required roles match the insider's roles
                insider_roles_set = set(insider.roles or [])
                alert_roles_set = set(alert.insider_roles)
                if not insider_roles_set.intersection(alert_roles_set):
                    return False

        # All criteria matched
        return True

    async def _recently_notified(
        self,
        alert_id: int,
        trade_id: int,
        cooldown_hours: int = 1
    ) -> bool:
        """
        Check if we've already sent a notification for this alert/trade combo recently.

        Prevents duplicate notifications.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=cooldown_hours)

        result = await self.db.execute(
            select(AlertHistory)
            .where(
                and_(
                    AlertHistory.alert_id == alert_id,
                    AlertHistory.trade_id == trade_id,
                    AlertHistory.created_at > cutoff_time
                )
            )
        )

        return result.scalar_one_or_none() is not None

    async def _trigger_alert_notifications(
        self,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str
    ) -> None:
        """
        Send notifications for a matched alert via all configured channels.

        Logs success/failure in alert_history.
        """
        logger.info(
            f"Alert triggered: {alert.name} (id={alert.id}) for trade {trade.id} "
            f"({trade.ticker})"
        )

        # Send notifications for each configured channel
        for channel in alert.notification_channels:
            if channel == "webhook" and alert.webhook_url:
                success, error = await self.notification_service.send_webhook_notification(
                    alert.webhook_url,
                    alert,
                    trade,
                    company_name,
                    insider_name
                )

                # Log to alert_history
                history = AlertHistory(
                    alert_id=alert.id,
                    trade_id=trade.id,
                    notification_channel="webhook",
                    notification_status="sent" if success else "failed",
                    error_message=error
                )
                self.db.add(history)

            elif channel == "email":
                # TODO: Phase 5B - Email notifications
                logger.info(f"Email notifications not yet implemented (alert={alert.name})")

            elif channel == "push":
                # TODO: Phase 5C - Push notifications
                logger.info(f"Push notifications not yet implemented (alert={alert.name})")

        await self.db.commit()

    async def send_test_notification(self, alert_id: int) -> tuple[bool, Optional[str]]:
        """
        Send a test notification for an alert.

        Returns (success, error_message).
        """
        alert = await self.get_alert(alert_id)
        if not alert:
            return False, "Alert not found"

        if "webhook" in alert.notification_channels and alert.webhook_url:
            return await self.notification_service.send_test_notification(
                alert.webhook_url,
                alert.name
            )

        return False, "No webhook configured for this alert"

    async def get_alert_history(
        self,
        alert_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[AlertHistory], int]:
        """Get alert trigger history with pagination."""
        query = select(AlertHistory)
        if alert_id:
            query = query.where(AlertHistory.alert_id == alert_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(AlertHistory.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        history = result.scalars().all()

        return list(history), total

    async def get_alert_stats(self) -> dict:
        """Get alert statistics."""
        # Total alerts
        total_result = await self.db.execute(select(func.count(Alert.id)))
        total_alerts = total_result.scalar() or 0

        # Active alerts
        active_result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.is_active == True)
        )
        active_alerts = active_result.scalar() or 0

        # Total notifications sent
        notifications_result = await self.db.execute(
            select(func.count(AlertHistory.id))
        )
        total_notifications = notifications_result.scalar() or 0

        # Notifications in last 24h
        cutoff_24h = datetime.utcnow() - timedelta(hours=24)
        recent_result = await self.db.execute(
            select(func.count(AlertHistory.id))
            .where(AlertHistory.created_at > cutoff_24h)
        )
        notifications_24h = recent_result.scalar() or 0

        # Failed notifications in last 24h
        failed_result = await self.db.execute(
            select(func.count(AlertHistory.id))
            .where(
                and_(
                    AlertHistory.created_at > cutoff_24h,
                    AlertHistory.notification_status == "failed"
                )
            )
        )
        failed_24h = failed_result.scalar() or 0

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "inactive_alerts": total_alerts - active_alerts,
            "total_notifications_sent": total_notifications,
            "notifications_last_24h": notifications_24h,
            "failed_notifications_last_24h": failed_24h,
        }
