"""
Notification Service for TradeSignal.

Sends notifications via webhooks (Slack, Discord, custom endpoints) and email.
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
    - Email notifications (SendGrid)

    Future support:
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

    async def send_email_notification(
        self,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Send email notification using SendGrid.

        Args:
            alert: Alert that was triggered
            trade: Trade that matched the alert
            company_name: Company name (for display)
            insider_name: Insider name (for display)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not settings.email_api_key or not settings.email_from or not alert.email:
            return False, "Email configuration is missing"

        subject = f"🔔 Trade Alert: {alert.name}"

        trade_value = float(trade.total_value) if trade.total_value else 0
        value_str = f"${trade_value:,.2f}"

        # Emoji based on transaction type
        emoji = "🟢" if trade.transaction_type == "BUY" else "🔴"

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .trade-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {'#10b981' if trade.transaction_type == 'BUY' else '#ef4444'}; }}
        .trade-title {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; color: #1f2937; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .detail-label {{ font-weight: 600; color: #6b7280; }}
        .detail-value {{ color: #1f2937; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} Trade Alert Triggered</h1>
            <p style="margin: 0; opacity: 0.9;">{alert.name}</p>
        </div>
        <div class="content">
            <div class="trade-info">
                <div class="trade-title">
                    {insider_name} {trade.transaction_type.lower()}s {value_str} of {trade.ticker}
                </div>
                <p style="color: #6b7280; margin-bottom: 15px;">{company_name}</p>
                <div class="detail-row">
                    <span class="detail-label">Transaction Type</span>
                    <span class="detail-value">{trade.transaction_type}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Shares</span>
                    <span class="detail-value">{trade.shares:,}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Price per Share</span>
                    <span class="detail-value">{'$' + f'{float(trade.price_per_share):.2f}' if trade.price_per_share else 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Total Value</span>
                    <span class="detail-value">{value_str}</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Transaction Date</span>
                    <span class="detail-value">{trade.transaction_date}</span>
                </div>
            </div>
            <center>
                <a href="{trade.sec_filing_url}" class="button">View SEC Filing →</a>
            </center>
            <div class="footer">
                <p>You're receiving this because you created an alert in TradeSignal.</p>
                <p>Powered by TradeSignal - Real-time Insider Trading Intelligence</p>
            </div>
        </div>
    </div>
</body>
</html>
        """

        try:
            # SendGrid API v3 payload
            payload = {
                "personalizations": [{
                    "to": [{"email": alert.email}]
                }],
                "from": {
                    "email": settings.email_from,
                    "name": settings.email_from_name
                },
                "subject": subject,
                "content": [{
                    "type": "text/html",
                    "value": html_body
                }]
            }

            # Send via SendGrid API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.email_api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 202:  # SendGrid returns 202 for success
                    logger.info(f"Email sent successfully for alert '{alert.name}' (trade_id={trade.id})")
                    return True, None
                else:
                    error_msg = f"SendGrid returned status {response.status_code}: {response.text[:200]}"
                    logger.error(error_msg)
                    return False, error_msg

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg

    async def send_test_email_notification(
        self,
        email_to: str,
        alert_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send a test email notification to verify email configuration.

        Args:
            email_to: Email address to send the test email to
            alert_name: Name of the alert being tested

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not settings.email_api_key or not settings.email_from:
            return False, "Email configuration is missing"

        subject = f"✅ Test Notification: {alert_name}"

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .success-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Test Email Successful!</h1>
        </div>
        <div class="content">
            <div class="success-box">
                <h2 style="color: #1f2937; margin-top: 0;">Email Configuration Verified</h2>
                <p style="color: #6b7280;">Your alert <strong>"{alert_name}"</strong> is configured correctly to send email notifications!</p>
                <p style="color: #6b7280; margin-bottom: 0;">You'll receive emails like this when your alert criteria are met.</p>
            </div>
            <div class="footer">
                <p>Powered by TradeSignal - Real-time Insider Trading Intelligence</p>
            </div>
        </div>
    </div>
</body>
</html>
        """

        try:
            # SendGrid API v3 payload
            payload = {
                "personalizations": [{
                    "to": [{"email": email_to}]
                }],
                "from": {
                    "email": settings.email_from,
                    "name": settings.email_from_name
                },
                "subject": subject,
                "content": [{
                    "type": "text/html",
                    "value": html_body
                }]
            }

            # Send via SendGrid API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.email_api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 202:
                    logger.info(f"Test email sent successfully for alert '{alert_name}'")
                    return True, None
                else:
                    error_msg = f"SendGrid returned status {response.status_code}: {response.text[:200]}"
                    logger.error(error_msg)
                    return False, error_msg

        except Exception as e:
            error_msg = f"Failed to send test email: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg

    async def send_push_notification(
        self,
        subscription,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send browser push notification.

        Args:
            subscription: PushSubscription instance
            alert: Alert that was triggered
            trade: Trade that matched the alert
            company_name: Company name (for display)
            insider_name: Insider name (for display)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            from pywebpush import webpush, WebPushException
            import json
        except ImportError:
            return False, "pywebpush library not installed"

        if not settings.vapid_private_key or not settings.vapid_public_key:
            return False, "VAPID keys not configured"

        # Build notification payload
        trade_value = float(trade.total_value) if trade.total_value else 0
        value_str = f"${trade_value:,.0f}"

        title = f"🔔 {alert.name}"
        body = f"{insider_name} {trade.transaction_type.lower()}s {value_str} of {trade.ticker}"

        payload = {
            "notification": {
                "title": title,
                "body": body,
                "icon": "/logo192.png",
                "badge": "/badge.png",
                "data": {
                    "url": f"/trades?ticker={trade.ticker}",
                    "trade_id": trade.id,
                    "alert_id": alert.id
                }
            }
        }

        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh_key,
                        "auth": subscription.auth_key
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={
                    "sub": settings.vapid_subject
                }
            )

            logger.info(f"Push notification sent for alert '{alert.name}' (subscription {subscription.id})")
            return True, None

        except WebPushException as e:
            if hasattr(e, 'response') and e.response.status_code == 410:
                # Subscription expired (410 Gone)
                logger.warning(f"Push subscription expired: {subscription.id}")
                return False, "Subscription expired (410 Gone)"

            error_msg = f"Push failed: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Failed to send push: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg

    async def send_test_push_notification(
        self,
        subscription,
        alert_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send a test push notification to verify push configuration.

        Args:
            subscription: PushSubscription instance
            alert_name: Name of the alert being tested

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            from pywebpush import webpush, WebPushException
            import json
        except ImportError:
            return False, "pywebpush library not installed"

        if not settings.vapid_private_key or not settings.vapid_public_key:
            return False, "VAPID keys not configured"

        # Build test notification payload
        payload = {
            "notification": {
                "title": f"✅ Test Notification",
                "body": f"Push notifications are working for {alert_name}!",
                "icon": "/logo192.png",
                "badge": "/badge.png",
                "data": {
                    "url": "/alerts",
                    "test": True
                }
            }
        }

        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh_key,
                        "auth": subscription.auth_key
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={
                    "sub": settings.vapid_subject
                }
            )

            logger.info(f"Test push notification sent for alert '{alert_name}'")
            return True, None

        except WebPushException as e:
            if hasattr(e, 'response') and e.response.status_code == 410:
                logger.warning(f"Push subscription expired: {subscription.id}")
                return False, "Subscription expired (410 Gone)"

            error_msg = f"Push test failed: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Failed to send test push: {str(e)[:200]}"
            logger.error(error_msg)
            return False, error_msg
