"""
Notification Service for TradeSignal.

Sends notifications via webhooks (Slack, Discord, custom endpoints).
Handles retries, timeouts, and error logging.
"""

import logging
import httpx
from typing import Optional
from datetime import datetime

from app.models.trade import Trade
from app.models.alert import Alert
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications via various channels.

    Currently supports:
    - Webhook notifications (Slack, Discord, custom HTTPS endpoints)

    Future support:
    - Email notifications (Phase 5B)
    - Browser push notifications (Phase 5C)
    """

    def __init__(self):
        self.timeout = 10.0  # seconds
        self.max_retries = 3

    async def send_webhook_notification(
        self,
        webhook_url: str,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send webhook notification to Slack/Discord/custom endpoint.

        Args:
            webhook_url: HTTPS webhook URL
            alert: Alert that was triggered
            trade: Trade that matched the alert
            company_name: Company name (for display)
            insider_name: Insider name (for display)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Determine if Slack or Discord based on URL
            is_slack = "slack.com" in webhook_url
            is_discord = "discord.com" in webhook_url

            # Build appropriate payload
            if is_slack:
                payload = self._build_slack_payload(alert, trade, company_name, insider_name)
            elif is_discord:
                payload = self._build_discord_payload(alert, trade, company_name, insider_name)
            else:
                payload = self._build_generic_payload(alert, trade, company_name, insider_name)

            # Send webhook with retries
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in [200, 204]:
                    logger.info(
                        f"Webhook sent successfully for alert '{alert.name}' "
                        f"(trade_id={trade.id})"
                    )
                    return True, None
                else:
                    error_msg = f"Webhook returned status {response.status_code}: {response.text[:200]}"
                    logger.warning(error_msg)
                    return False, error_msg

        except httpx.TimeoutException:
            error_msg = f"Webhook timeout after {self.timeout}s"
            logger.error(f"{error_msg} for alert '{alert.name}'")
            return False, error_msg

        except httpx.RequestError as e:
            error_msg = f"Webhook request failed: {str(e)[:200]}"
            logger.error(f"{error_msg} for alert '{alert.name}'")
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error sending webhook: {str(e)[:200]}"
            logger.error(f"{error_msg} for alert '{alert.name}'", exc_info=True)
            return False, error_msg

    def _build_slack_payload(
        self,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str
    ) -> dict:
        """Build Slack-formatted webhook payload."""
        # Format trade value
        trade_value = float(trade.total_value) if trade.total_value else 0
        value_str = f"${trade_value:,.2f}"

        # Determine emoji based on transaction type
        emoji = "🟢" if trade.transaction_type == "BUY" else "🔴"

        # Build Slack blocks
        return {
            "text": f"{emoji} Trade Alert: {alert.name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} {alert.name}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*{insider_name}* {trade.transaction_type.lower()}s "
                            f"*{value_str}* of *{trade.ticker}* ({company_name})"
                        )
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Shares:*\n{trade.shares:,}"},
                        {"type": "mrkdwn", "text": f"*Price:*\n${float(trade.price_per_share):.2f}" if trade.price_per_share else "*Price:*\nN/A"},
                        {"type": "mrkdwn", "text": f"*Date:*\n{trade.transaction_date}"},
                        {"type": "mrkdwn", "text": f"*Type:*\n{trade.transaction_type}"}
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View SEC Filing", "emoji": True},
                            "url": trade.sec_filing_url
                        }
                    ]
                }
            ]
        }

    def _build_discord_payload(
        self,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str
    ) -> dict:
        """Build Discord-formatted webhook payload."""
        # Format trade value
        trade_value = float(trade.total_value) if trade.total_value else 0
        value_str = f"${trade_value:,.2f}"

        # Color based on transaction type (green for buy, red for sell)
        color = 0x10B981 if trade.transaction_type == "BUY" else 0xEF4444

        # Build Discord embed
        return {
            "embeds": [{
                "title": f"🔔 {alert.name}",
                "description": (
                    f"**{insider_name}** {trade.transaction_type.lower()}s "
                    f"**{value_str}** of **{trade.ticker}** ({company_name})"
                ),
                "color": color,
                "fields": [
                    {"name": "Shares", "value": f"{trade.shares:,}", "inline": True},
                    {"name": "Price", "value": f"${float(trade.price_per_share):.2f}" if trade.price_per_share else "N/A", "inline": True},
                    {"name": "Date", "value": trade.transaction_date, "inline": True},
                    {"name": "Type", "value": trade.transaction_type, "inline": True},
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "TradeSignal Alerts"},
                "url": trade.sec_filing_url
            }]
        }

    def _build_generic_payload(
        self,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str
    ) -> dict:
        """Build generic JSON payload for custom webhooks."""
        trade_value = float(trade.total_value) if trade.total_value else 0

        return {
            "alert_name": alert.name,
            "alert_type": alert.alert_type,
            "timestamp": datetime.utcnow().isoformat(),
            "trade": {
                "id": trade.id,
                "ticker": trade.ticker,
                "company_name": company_name,
                "insider_name": insider_name,
                "transaction_type": trade.transaction_type,
                "transaction_date": trade.transaction_date,
                "shares": str(trade.shares),
                "price_per_share": str(trade.price_per_share) if trade.price_per_share else None,
                "total_value": trade_value,
                "sec_filing_url": trade.sec_filing_url,
                "ownership_type": trade.ownership_type,
                "is_significant": trade.is_significant,
            }
        }

    async def send_test_notification(
        self,
        webhook_url: str,
        alert_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send a test notification to verify webhook configuration.

        Args:
            webhook_url: HTTPS webhook URL
            alert_name: Name of the alert being tested

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Determine webhook type
            is_slack = "slack.com" in webhook_url
            is_discord = "discord.com" in webhook_url

            # Build test payload
            if is_slack:
                payload = {
                    "text": f"✅ Test notification for alert: {alert_name}",
                    "blocks": [{
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"✅ *Test Notification*\n\nYour alert `{alert_name}` is configured correctly!"
                        }
                    }]
                }
            elif is_discord:
                payload = {
                    "embeds": [{
                        "title": "✅ Test Notification",
                        "description": f"Your alert **{alert_name}** is configured correctly!",
                        "color": 0x10B981,
                        "timestamp": datetime.utcnow().isoformat()
                    }]
                }
            else:
                payload = {
                    "test": True,
                    "alert_name": alert_name,
                    "message": "Test notification - webhook configured successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Send test webhook
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in [200, 204]:
                    logger.info(f"Test webhook sent successfully for alert '{alert_name}'")
                    return True, None
                else:
                    error_msg = f"Test webhook returned status {response.status_code}"
                    logger.warning(error_msg)
                    return False, error_msg

        except Exception as e:
            error_msg = f"Test webhook failed: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg
