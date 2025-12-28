"""
Notification Service for TradeSignal.

Handles notifications via webhooks, email, and web push.
NOTE: Celery tasks removed - notifications are disabled until direct implementation.
"""

import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.trade import Trade
from app.models.alert import Alert
from app.models.push_subscription import PushSubscription
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for enqueuing notification tasks via various channels.
    """

    def __init__(self):
        # No direct external clients needed anymore
        pass

    async def send_webhook_notification(
        self,
        webhook_url: str,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str,
    ) -> Dict[str, Any]:
        """
        Enqueue task to send webhook notification.
        """
        trade_data = trade.to_dict() # Assuming a .to_dict() method or manual serialization
        alert_name = alert.name # Assuming alert.name exists
        
        # NOTE: Celery tasks removed - webhook notifications disabled
        logger.info(f"Webhook notification requested (Celery disabled): {webhook_url}")
        return {"status": "disabled", "message": "Background tasks disabled"}

    async def _build_email_html_body(
        self, alert: Alert, trade: Trade, company_name: str, insider_name: str
    ) -> str:
        """Helper to build the HTML body for trade alert emails."""
        trade_value = float(trade.total_value) if trade.total_value else 0
        value_str = f"${trade_value:,.2f}"
        emoji = "🟢" if trade.transaction_type == "BUY" else "🔴"

        # Simplified for brevity, will use the full template from original _send_email_notification
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
               Roboto, Helvetica, Arial, sans-serif; line-height: 1.6;
               color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%,
                   #764ba2 100%); color: white; padding: 30px;
                   border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f9fafb; padding: 30px;
                    border-radius: 0 0 10px 10px; }}
        .trade-info {{ background: white; padding: 20px; border-radius: 8px;
                       margin: 20px 0; border-left: 4px solid
                       {'#10b981' if trade.transaction_type == 'BUY'
                       else '#ef4444'}; }}
        .trade-title {{ font-size: 20px; font-weight: bold;
                        margin-bottom: 15px; color: #1f2937; }}
        .detail-row {{ display: flex; justify-content: space-between;
                       padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .detail-label {{ font-weight: 600; color: #6b7280; }}
        .detail-value {{ color: #1f2937; }}
        .button {{ display: inline-block; background: #667eea; color: white;
                   padding: 12px 30px; text-decoration: none;
                   border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px;
                   margin-top: 30px; }}
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
                    <span class="detail-value">
                        {'$' + f'{float(trade.price_per_share):.2f}' if trade.price_per_share else 'N/A'}
                    </span>
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

    async def send_email_notification(
        self,
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str,
    ) -> Dict[str, Any]:
        """
        Enqueue task to send email notification using SendGrid.
        """
        if not settings.email_api_key or not settings.email_from or not alert.email:
            logger.warning(f"Email configuration missing or alert email not set for alert {alert.id}. Skipping email notification.")
            return {"status": "skipped", "channel": "email", "error": "Email configuration missing"}

        subject = f"🔔 Trade Alert: {alert.name}"
        html_body = await self._build_email_html_body(alert, trade, company_name, insider_name)
        
        # NOTE: Celery tasks removed - email notifications disabled
        logger.info(f"Email notification requested (Celery disabled): {alert.email}")
        return {"status": "disabled", "message": "Background tasks disabled"}

    async def send_subscription_confirmation_email(
        self, email_to: str, tier: str, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """
        Enqueue task to send subscription confirmation email.
        """
        if not settings.email_api_key or not settings.email_from:
            logger.warning("Email configuration is missing. Skipping subscription confirmation email.")
            return {"status": "skipped", "channel": "email", "error": "Email configuration missing"}

        tier_names = {"basic": "Basic", "pro": "Pro", "enterprise": "Enterprise"}
        tier_name = tier_names.get(tier.lower(), tier.capitalize())
        subject = f"🎉 Welcome to TradeSignal {tier_name}!"

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
               Roboto, Helvetica, Arial, sans-serif; line-height: 1.6;
               color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%,
                   #764ba2 100%); color: white; padding: 30px;
                   border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f9fafb; padding: 30px;
                    border-radius: 0 0 10px 10px; }}
        .info-box {{ background: white; padding: 20px; border-radius: 8px;
                     margin: 20px 0; border-left: 4px solid #667eea; }}
        .detail-row {{ display: flex; justify-content: space-between;
                       padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .detail-label {{ font-weight: 600; color: #6b7280; }}
        .detail-value {{ color: #1f2937; }}
        .button {{ display: inline-block; background: #667eea; color: white;
                   padding: 12px 30px; text-decoration: none;
                   border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px;
                   margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to TradeSignal {tier_name}!</h1>
            <p style="margin: 0; opacity: 0.9;">Your subscription has been activated</p>
        </div>
        <div class="content">
            <div class="info-box">
                <h2 style="color: #1f2937; margin-top: 0;">Subscription Details</h2>
                <div class="detail-row">
                    <span class="detail-label">Plan</span>
                    <span class="detail-value"><strong>{tier_name}</strong></span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Billing Period</span>
                    <span class="detail-value">{period_start.strftime('%B %d, %Y')} - {period_end.strftime('%B %d, %Y')}</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Next Renewal</span>
                    <span class="detail-value">{period_end.strftime('%B %d, %Y')}</span>
                </div>
            </div>
            <p style="color: #6b7280;">Thank you for subscribing to TradeSignal {tier_name}! You now have access to:</p>
            <ul style="color: #6b7280;">
                <li>Enhanced insider trading data and analytics</li>
                <li>Real-time alerts and notifications</li>
                <li>Advanced AI-powered insights</li>
                <li>Priority support</li>
            </ul>
            <center>
                <a href="{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard" class="button">Go to Dashboard →</a>
            </center>
            <div class="footer">
                <p>You're receiving this because you successfully subscribed to TradeSignal {tier_name}.</p>
                <p>Powered by TradeSignal - Real-time Insider Trading Intelligence</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # NOTE: Celery tasks removed - email notifications disabled
        logger.info(f"Subscription confirmation email requested (Celery disabled): {email_to}")
        return {"status": "disabled", "message": "Background tasks disabled"}

    async def send_test_email_notification(
        self, email_to: str, alert_name: str
    ) -> Dict[str, Any]:
        """
        Enqueue task to send a test email notification.
        """
        if not settings.email_api_key or not settings.email_from:
            logger.warning("Email configuration is missing. Skipping test email notification.")
            return {"status": "skipped", "channel": "email", "error": "Email configuration missing"}

        subject = f"✅ Test Notification: {alert_name}"

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
               Roboto, Helvetica, Arial, sans-serif; line-height: 1.6;
               color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%,
                   #059669 100%); color: white; padding: 30px;
                   border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f9fafb; padding: 30px;
                    border-radius: 0 0 10px 10px; }}
        .success-box {{ background: white; padding: 20px;
                        border-radius: 8px; margin: 20px 0;
                        border-left: 4px solid #10b981; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px;
                   margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Test Email Successful!</h1>
        </div>
        <div class="content">
            <div class="success-box">
                <h2 style="color: #1f2937; margin-top: 0;">
                    Email Configuration Verified
                </h2>
                <p style="color: #6b7280;">
                    Your alert <strong>"{alert_name}"</strong> is configured
                    correctly to send email notifications!
                </p>
                <p style="color: #6b7280; margin-bottom: 0;">
                    You'll receive emails like this when your alert criteria
                    are met.
                </p>
            </div>
            <div class="footer">
                <p>Powered by TradeSignal - Real-time Insider Trading Intelligence</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # NOTE: Celery tasks removed - email notifications disabled
        logger.info(f"Test email notification requested (Celery disabled): {email_to}")
        return {"status": "disabled", "message": "Background tasks disabled"}

    async def send_push_notification(
        self,
        subscription: PushSubscription, # PushSubscription object
        alert: Alert,
        trade: Trade,
        company_name: str,
        insider_name: str,
    ) -> Dict[str, Any]:
        """
        Enqueue task to send browser push notification.
        """
        # PushSubscription object needs to be serialized
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh_key,
                "auth": subscription.auth_key,
            },
        }
        trade_data = trade.to_dict() # Serialize trade object
        alert_name = alert.name # Serialize alert name
        alert_id = alert.id # Pass alert id
        
        # NOTE: Celery tasks removed - push notifications disabled
        logger.info(f"Push notification requested (Celery disabled): alert {alert_id}")
        return {"status": "disabled", "message": "Background tasks disabled"}

    async def send_test_push_notification(
        self, subscription: PushSubscription, alert_name: str
    ) -> Dict[str, Any]:
        """
        Enqueue task to send a test push notification.
        """
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh_key,
                "auth": subscription.auth_key,
            },
        }
        
        # NOTE: Celery tasks removed - push notifications disabled
        logger.info(f"Test push notification requested (Celery disabled): {alert_name}")
        return {"status": "disabled", "message": "Background tasks disabled"}

