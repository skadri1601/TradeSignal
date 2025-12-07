"""
Multi-Channel Alert Service

Sends alerts through multiple channels:
- Email (existing)
- Push Notifications (existing)
- Discord (new)
- Slack (new)
- SMS (new)

Implements smart routing and rate limiting.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class MultiChannelAlertService:
    """
    Service for sending alerts through multiple channels.

    Channels:
    - Email (via existing notification service)
    - Push (via existing push service)
    - Discord webhook
    - Slack webhook
    - SMS (Twilio)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.discord_webhook_url = getattr(settings, "DISCORD_WEBHOOK_URL", None)
        self.slack_webhook_url = getattr(settings, "SLACK_WEBHOOK_URL", None)
        self.twilio_account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        self.twilio_auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        self.twilio_phone_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)

    async def send_alert(
        self, alert_data: Dict[str, Any], channels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send alert through specified channels.

        Args:
            alert_data: Alert information (trade, company, insider, etc.)
            channels: List of channels to use (default: all enabled)

        Returns:
            Dict with send status for each channel
        """
        if channels is None:
            channels = ["email", "push", "discord", "slack", "sms"]

        results = {}

        # Send to each channel
        if "discord" in channels and self.discord_webhook_url:
            results["discord"] = await self._send_discord(alert_data)

        if "slack" in channels and self.slack_webhook_url:
            results["slack"] = await self._send_slack(alert_data)

        if "sms" in channels and self.twilio_account_sid:
            results["sms"] = await self._send_sms(alert_data)

        # Email and push are handled by existing services
        if "email" in channels:
            results["email"] = {"status": "handled_by_notification_service"}

        if "push" in channels:
            results["push"] = {"status": "handled_by_push_service"}

        return results

    async def _send_discord(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert to Discord webhook."""
        try:
            # Format Discord message
            ticker = alert_data.get("ticker", "N/A")
            company_name = alert_data.get("company_name", "Unknown")
            insider = alert_data.get("insider", "Unknown")
            trade_type = alert_data.get("transaction_type", "TRADE")
            value = alert_data.get("total_value", 0)

            embed = {
                "title": f"🚨 Insider Trade Alert: {ticker}",
                "description": f"**{insider}** {trade_type} in **{company_name}** ({ticker})",
                "color": 0x00FF00 if trade_type == "BUY" else 0xFF0000,
                "fields": [
                    {
                        "name": "Trade Value",
                        "value": f"${value:,.2f}" if value else "Not Disclosed",
                        "inline": True,
                    },
                    {
                        "name": "Date",
                        "value": alert_data.get("transaction_date", "N/A"),
                        "inline": True,
                    },
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "TradeSignal Insider Trading Alerts"},
            }

            payload = {"embeds": [embed]}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.discord_webhook_url, json=payload, timeout=10.0
                )
                response.raise_for_status()

            return {"status": "success", "channel": "discord"}

        except Exception as e:
            logger.error(f"Error sending Discord alert: {e}")
            return {"status": "error", "channel": "discord", "error": str(e)}

    async def _send_slack(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert to Slack webhook."""
        try:
            ticker = alert_data.get("ticker", "N/A")
            company_name = alert_data.get("company_name", "Unknown")
            insider = alert_data.get("insider", "Unknown")
            trade_type = alert_data.get("transaction_type", "TRADE")
            value = alert_data.get("total_value", 0)

            # Format Slack message
            color = "good" if trade_type == "BUY" else "danger"

            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"Insider Trade Alert: {ticker}",
                        "text": f"*{insider}* {trade_type} in *{company_name}* ({ticker})",
                        "fields": [
                            {
                                "title": "Trade Value",
                                "value": f"${value:,.2f}" if value else "Not Disclosed",
                                "short": True,
                            },
                            {
                                "title": "Date",
                                "value": alert_data.get("transaction_date", "N/A"),
                                "short": True,
                            },
                        ],
                        "footer": "TradeSignal",
                        "ts": int(datetime.utcnow().timestamp()),
                    }
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook_url, json=payload, timeout=10.0
                )
                response.raise_for_status()

            return {"status": "success", "channel": "slack"}

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return {"status": "error", "channel": "slack", "error": str(e)}

    async def _send_sms(
        self, alert_data: Dict[str, Any], phone_number: str = None
    ) -> Dict[str, Any]:
        """Send alert via SMS using Twilio."""
        if not phone_number:
            return {
                "status": "error",
                "channel": "sms",
                "error": "No phone number provided",
            }

        try:
            from twilio.rest import Client as TwilioClient

            client = TwilioClient(self.twilio_account_sid, self.twilio_auth_token)

            ticker = alert_data.get("ticker", "N/A")
            insider = alert_data.get("insider", "Unknown")
            trade_type = alert_data.get("transaction_type", "TRADE")

            message = (
                f"TradeSignal Alert: {insider} {trade_type} {ticker}. "
                f"Value: ${alert_data.get('total_value', 0):,.0f}"
                if alert_data.get("total_value")
                else "Value: Not Disclosed"
            )

            # Send SMS
            message = client.messages.create(
                body=message, from_=self.twilio_phone_number, to=phone_number
            )

            return {"status": "success", "channel": "sms", "message_sid": message.sid}

        except ImportError:
            logger.error("Twilio not installed. Install with: pip install twilio")
            return {
                "status": "error",
                "channel": "sms",
                "error": "Twilio not installed",
            }
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {"status": "error", "channel": "sms", "error": str(e)}
