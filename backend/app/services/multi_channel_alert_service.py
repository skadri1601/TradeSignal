"""
Multi-Channel Alert Service

Sends alerts through multiple channels by enqueuing Celery tasks:
- Email (existing - handled by another service, not this one)
- Push Notifications (existing - handled by another service, not this one)
- Discord (new - via Celery task)
- Slack (new - via Celery task)
- SMS (new - via Celery task)

Also enqueues in-app notification creation.
"""

import logging
from typing import List, Dict, Any
from app.tasks.alert_tasks import send_discord_alert_task, send_slack_alert_task, send_sms_alert_task, create_in_app_notification_task
from app.schemas.notification import NotificationCreate # For serializing to pass to task

logger = logging.getLogger(__name__)


class MultiChannelAlertService:
    """
    Service for sending alerts through multiple channels by enqueuing Celery tasks.
    """

    def __init__(self):
        # No longer needs db or notification_storage_service directly for external sends
        pass

    async def send_alert(
        self, alert_data: Dict[str, Any], user_id: int, channels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Enqueue tasks to send alerts through specified channels and create an in-app notification.

        Args:
            alert_data: Alert information (trade, company, insider, etc.)
            user_id: The ID of the user who owns the alert.
            channels: List of channels to use (default: all possible)

        Returns:
            Dict with status for each enqueued channel
        """
        if channels is None:
            channels = ["discord", "slack", "sms"] # Email and push are handled by other services

        results = {}

        # Enqueue tasks for external channels
        if "discord" in channels:
            task = send_discord_alert_task.delay(alert_data)
            results["discord"] = {"status": "enqueued", "task_id": task.id}
            logger.info(f"Discord alert task enqueued with ID: {task.id}")

        if "slack" in channels:
            task = send_slack_alert_task.delay(alert_data)
            results["slack"] = {"status": "enqueued", "task_id": task.id}
            logger.info(f"Slack alert task enqueued with ID: {task.id}")

        if "sms" in channels:
            phone_number = alert_data.get("phone_number") # Phone number must be in alert_data
            if phone_number:
                task = send_sms_alert_task.delay(alert_data, phone_number)
                results["sms"] = {"status": "enqueued", "task_id": task.id}
                logger.info(f"SMS alert task enqueued with ID: {task.id} to {phone_number}")
            else:
                results["sms"] = {"status": "skipped", "error": "No phone number provided for SMS"}
                logger.warning("SMS alert skipped: No phone number in alert_data.")

        # Enqueue task for in-app notification
        try:
            notification_title = f"Alert: {alert_data.get('company_ticker', 'N/A')} {alert_data.get('transaction_type', 'Trade')} by {alert_data.get('insider', 'N/A')}"
            notification_message = (
                f"An insider trade matching your criteria occurred: {alert_data.get('insider', 'Unknown')} "
                f"{'bought' if alert_data.get('transaction_type') == 'BUY' else 'sold'} "
                f"${alert_data.get('total_value', 0):,.0f} worth of {alert_data.get('company_name', 'Unknown')} ({alert_data.get('ticker', 'N/A')})."
            )
            notification_payload = NotificationCreate(
                user_id=user_id,
                alert_id=alert_data.get("alert_id"),
                type="alert",
                title=notification_title,
                message=notification_message,
                data={
                    "ticker": alert_data.get("ticker"),
                    "trade_id": alert_data.get("trade_id"),
                    "link": f"/trades/{alert_data.get('trade_id')}" if alert_data.get("trade_id") else "/alerts",
                },
            ).model_dump() # Convert to dict for Celery task
            
            task = create_in_app_notification_task.delay(notification_payload)
            results["in_app"] = {"status": "enqueued", "task_id": task.id}
            logger.info(f"In-app notification task enqueued with ID: {task.id}")

        except Exception as e:
            logger.error(f"Error enqueuing in-app notification task for user {user_id}: {e}", exc_info=True)
            results["in_app"] = {"status": "error", "error": str(e)}

        return results
