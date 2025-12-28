"""
Multi-Channel Alert Service

Sends alerts through multiple channels.
NOTE: Celery tasks removed - alerts logged but not sent to external channels.
Future: Implement direct webhook calls for Discord/Slack.
"""

import logging
from typing import List, Dict, Any
from app.schemas.notification import NotificationCreate

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
        # NOTE: Celery tasks removed - alert channels disabled
        # Future: Implement direct webhook calls for Discord/Slack
        
        if "discord" in channels:
            logger.info(f"Discord alert requested (Celery disabled): {alert_data.get('ticker', 'N/A')}")
            results["discord"] = {"status": "disabled", "message": "Background tasks disabled"}

        if "slack" in channels:
            logger.info(f"Slack alert requested (Celery disabled): {alert_data.get('ticker', 'N/A')}")
            results["slack"] = {"status": "disabled", "message": "Background tasks disabled"}

        if "sms" in channels:
            phone_number = alert_data.get("phone_number")
            if phone_number:
                logger.info(f"SMS alert requested (Celery disabled): {phone_number}")
                results["sms"] = {"status": "disabled", "message": "Background tasks disabled"}
            else:
                results["sms"] = {"status": "skipped", "error": "No phone number provided for SMS"}

        # In-app notification - log for now
        try:
            notification_title = f"Alert: {alert_data.get('company_ticker', 'N/A')} {alert_data.get('transaction_type', 'Trade')} by {alert_data.get('insider', 'N/A')}"
            logger.info(f"In-app notification requested (Celery disabled): {notification_title}")
            results["in_app"] = {"status": "disabled", "message": "Background tasks disabled"}
        except Exception as e:
            logger.error(f"Error creating in-app notification for user {user_id}: {e}", exc_info=True)
            results["in_app"] = {"status": "error", "error": str(e)}

        return results
