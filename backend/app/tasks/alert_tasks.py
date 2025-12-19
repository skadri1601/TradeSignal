from app.core.celery_app import celery_app
import logging
import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.services.notification_storage_service import NotificationStorageService
from app.schemas.notification import NotificationCreate # For serializing to pass to task
from app.database import db_manager # For NotificationStorageService if needed
from datetime import datetime, date
import os # For FRONTEND_URL in email templates

logger = logging.getLogger(__name__)

# For push notifications
try:
    from pywebpush import webpush, WebPushException
    import json
except ImportError:
    webpush = None
    WebPushException = None
    json = None
    logger.warning("pywebpush not installed. Push notifications will be disabled.")

# --- Tasks for MultiChannelAlertService ---

@celery_app.task(name="send_discord_alert")
async def send_discord_alert_task(alert_data: Dict[str, Any]):
    """Celery task to send an alert to Discord webhook."""
    discord_webhook_url = settings.discord_webhook_url
    if not discord_webhook_url:
        logger.warning("Discord webhook URL not configured. Skipping Discord alert.")
        return {"status": "skipped", "channel": "discord", "error": "Webhook URL not configured"}

    try:
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

        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            response = await client.post(discord_webhook_url, json=payload)
            response.raise_for_status()

        logger.info(f"Successfully sent Discord alert for {ticker}.")
        return {"status": "success", "channel": "discord"}

    except httpx.HTTPStatusError as e:
        logger.error(f"Error sending Discord alert (HTTP {e.response.status_code}): {e.response.text}")
        return {"status": "error", "channel": "discord", "error": str(e)}
    except httpx.RequestError as e:
        logger.error(f"Request error sending Discord alert: {e}")
        return {"status": "error", "channel": "discord", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending Discord alert: {e}", exc_info=True)
        return {"status": "error", "channel": "discord", "error": str(e)}

@celery_app.task(name="send_slack_alert")
async def send_slack_alert_task(alert_data: Dict[str, Any]):
    """Celery task to send an alert to Slack webhook."""
    slack_webhook_url = settings.slack_webhook_url
    if not slack_webhook_url:
        logger.warning("Slack webhook URL not configured. Skipping Slack alert.")
        return {"status": "skipped", "channel": "slack", "error": "Webhook URL not configured"}

    try:
        ticker = alert_data.get("ticker", "N/A")
        company_name = alert_data.get("company_name", "Unknown")
        insider = alert_data.get("insider", "Unknown")
        trade_type = alert_data.get("transaction_type", "TRADE")
        value = alert_data.get("total_value", 0)

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

        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            response = await client.post(slack_webhook_url, json=payload)
            response.raise_for_status()

        logger.info(f"Successfully sent Slack alert for {ticker}.")
        return {"status": "success", "channel": "slack"}

    except httpx.HTTPStatusError as e:
        logger.error(f"Error sending Slack alert (HTTP {e.response.status_code}): {e.response.text}")
        return {"status": "error", "channel": "slack", "error": str(e)}
    except httpx.RequestError as e:
        logger.error(f"Request error sending Slack alert: {e}")
        return {"status": "error", "channel": "slack", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending Slack alert: {e}", exc_info=True)
        return {"status": "error", "channel": "slack", "error": str(e)}

@celery_app.task(name="send_sms_alert")
async def send_sms_alert_task(alert_data: Dict[str, Any], phone_number: str):
    """Celery task to send an alert via SMS using Twilio."""
    twilio_account_sid = settings.twilio_account_sid
    twilio_auth_token = settings.twilio_auth_token
    twilio_phone_number = settings.twilio_phone_number

    if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        logger.warning("Twilio credentials not fully configured. Skipping SMS alert.")
        return {"status": "skipped", "channel": "sms", "error": "Twilio not configured"}
    if not phone_number:
        logger.warning("No phone number provided for SMS alert. Skipping SMS.")
        return {"status": "skipped", "channel": "sms", "error": "No phone number provided"}

    try:
        from twilio.rest import Client as TwilioClient
        client = TwilioClient(twilio_account_sid, twilio_auth_token)

        ticker = alert_data.get("ticker", "N/A")
        insider = alert_data.get("insider", "Unknown")
        trade_type = alert_data.get("transaction_type", "TRADE")

        message_body = (
            f"TradeSignal Alert: {insider} {trade_type} {ticker}. "
            f"Value: ${alert_data.get('total_value', 0):,.0f}"
            if alert_data.get("total_value")
            else "Value: Not Disclosed"
        )

        message = client.messages.create(
            body=message_body, from_=twilio_phone_number, to=phone_number
        )

        logger.info(f"Successfully sent SMS alert to {phone_number} for {ticker}. SID: {message.sid}")
        return {"status": "success", "channel": "sms", "message_sid": message.sid}

    except ImportError:
        logger.error("Twilio not installed. Install with: pip install twilio")
        return {"status": "error", "channel": "sms", "error": "Twilio not installed"}
    except Exception as e:
        logger.error(f"Error sending SMS to {phone_number}: {e}", exc_info=True)
        return {"status": "error", "channel": "sms", "error": str(e)}

@celery_app.task(name="create_in_app_notification")
async def create_in_app_notification_task(notification_data: Dict[str, Any]):
    """Celery task to create an in-app notification via NotificationStorageService."""
    try:
        # NotificationStorageService needs a db session. We get it from db_manager
        async with db_manager.get_session() as db:
            notification_storage_service = NotificationStorageService(db)
            notification_create = NotificationCreate(**notification_data)
            await notification_storage_service.create_notification(notification_create)
            logger.info(f"Successfully created in-app notification for user {notification_data.get('user_id')}.")
            return {"status": "success", "channel": "in_app"}
    except Exception as e:
        logger.error(f"Error creating in-app notification for user {notification_data.get('user_id')}: {e}", exc_info=True)
        return {"status": "error", "channel": "in_app", "error": str(e)}


# --- Tasks for NotificationService ---

@celery_app.task(name="send_webhook_notification")
async def send_webhook_notification_task(
    webhook_url: str,
    alert_name: str, # Using alert name instead of Alert object for serialization
    trade_data: Dict[str, Any], # Using trade data instead of Trade object for serialization
    company_name: str,
    insider_name: str,
):
    """Celery task to send a generic webhook notification."""
    try:
        # Helper functions to build payloads (can be moved to a shared utility or re-implemented here)
        def _build_slack_payload(alert_name, trade, company_name, insider_name) -> dict:
            trade_value = float(trade.get("total_value", 0))
            value_str = f"${trade_value:,.2f}"
            emoji = "🟢" if trade.get("transaction_type") == "BUY" else "🔴"

            return {
                "text": f"{emoji} Trade Alert: {alert_name}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} {alert_name}",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*{insider_name}* {trade.get('transaction_type').lower()}s "
                                f"*{value_str}* of *{trade.get('ticker')}* ({company_name})"
                            ),
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Shares:*\n{trade.get('shares',0):,}"},
                            {
                                "type": "mrkdwn",
                                "text": f"*Price:*\n${float(trade.get('price_per_share',0)):.2f}"
                                if trade.get("price_per_share")
                                else "*Price:*\nN/A",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Date:*\n{trade.get('transaction_date')}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Type:*\n{trade.get('transaction_type')}",
                            },
                        ],
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View SEC Filing",
                                    "emoji": True,
                                },
                                "url": trade.get("sec_filing_url"),
                            }
                        ],
                    },
                ],
            }

        def _build_discord_payload(alert_name, trade, company_name, insider_name) -> dict:
            trade_value = float(trade.get("total_value", 0))
            value_str = f"${trade_value:,.2f}"
            color = 0x10B981 if trade.get("transaction_type") == "BUY" else 0xEF4444

            return {
                "embeds": [
                    {
                        "title": f"🔔 {alert_name}",
                        "description": (
                            f"**{insider_name}** {trade.get('transaction_type').lower()}s "
                            f"**{value_str}** of **{trade.get('ticker')}** ({company_name})"
                        ),
                        "color": color,
                        "fields": [
                            {
                                "name": "Shares",
                                "value": f"{trade.get('shares',0):,}",
                                "inline": True,
                            },
                            {
                                "name": "Price",
                                "value": f"${float(trade.get('price_per_share',0)):.2f}"
                                if trade.get("price_per_share")
                                else "N/A",
                                "inline": True,
                            },
                            {
                                "name": "Date",
                                "value": trade.get("transaction_date"),
                                "inline": True,
                            },
                            {
                                "name": "Type",
                                "value": trade.get("transaction_type"),
                                "inline": True,
                            },
                        ],
                        "timestamp": datetime.utcnow().isoformat(),
                        "footer": {"text": "TradeSignal Alerts"},
                        "url": trade.get("sec_filing_url"),
                    }
                ]
            }

        def _build_generic_payload(alert_name, trade, company_name, insider_name) -> dict:
            trade_value = float(trade.get("total_value", 0))

            return {
                "alert_name": alert_name,
                "timestamp": datetime.utcnow().isoformat(),
                "trade": {
                    "id": trade.get("id"),
                    "ticker": trade.get("ticker"),
                    "company_name": company_name,
                    "insider_name": insider_name,
                    "transaction_type": trade.get("transaction_type"),
                    "transaction_date": trade.get("transaction_date"),
                    "shares": str(trade.get("shares")),
                    "price_per_share": str(trade.get("price_per_share"))
                    if trade.get("price_per_share")
                    else None,
                    "total_value": trade_value,
                    "sec_filing_url": trade.get("sec_filing_url"),
                    "ownership_type": trade.get("ownership_type"),
                    "is_significant": trade.get("is_significant"),
                },
            }

        # Detect webhook type from URL
        is_slack = "slack.com" in webhook_url
        is_discord = "discord.com" in webhook_url

        # Build appropriate payload
        if is_slack:
            payload = _build_slack_payload(alert_name, trade_data, company_name, insider_name)
        elif is_discord:
            payload = _build_discord_payload(alert_name, trade_data, company_name, insider_name)
        else:
            payload = _build_generic_payload(alert_name, trade_data, company_name, insider_name)

        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

        logger.info(f"Webhook sent successfully for alert '{alert_name}' (trade_id={trade_data.get('id')}).")
        return {"status": "success", "channel": "webhook"}

    except httpx.HTTPStatusError as e:
        logger.error(f"Webhook returned status {e.response.status_code}: {e.response.text[:200]}")
        return {"status": "error", "channel": "webhook", "error": str(e)}
    except httpx.RequestError as e:
        logger.error(f"Webhook request failed: {str(e)[:200]}")
        return {"status": "error", "channel": "webhook", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending webhook: {str(e)[:200]}", exc_info=True)
        return {"status": "error", "channel": "webhook", "error": str(e)}

@celery_app.task(name="send_test_webhook_notification")
async def send_test_webhook_notification_task(webhook_url: str, alert_name: str):
    """Celery task to send a test webhook notification."""
    try:
        is_slack = "slack.com" in webhook_url
        is_discord = "discord.com" in webhook_url

        if is_slack:
            payload = {
                "text": f"✅ Test notification for alert: {alert_name}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"✅ *Test Notification*\n\nYour alert `{alert_name}` is configured correctly!",
                        },
                    }
                ],
            }
        elif is_discord:
            payload = {
                "embeds": [
                    {
                        "title": "✅ Test Notification",
                        "description": f"Your alert **{alert_name}** is configured correctly!",
                        "color": 0x10B981,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ]
            }
        else:
            payload = {
                "test": True,
                "alert_name": alert_name,
                "message": "Test notification - webhook configured successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }

        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

        logger.info(f"Test webhook sent successfully for alert '{alert_name}'.")
        return {"status": "success", "channel": "test_webhook"}

    except httpx.HTTPStatusError as e:
        logger.error(f"Test webhook returned status {e.response.status_code}: {e.response.text[:200]}")
        return {"status": "error", "channel": "test_webhook", "error": str(e)}
    except httpx.RequestError as e:
        logger.error(f"Test webhook request failed: {str(e)[:200]}")
        return {"status": "error", "channel": "test_webhook", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending test webhook: {str(e)[:200]}", exc_info=True)
        return {"status": "error", "channel": "test_webhook", "error": str(e)}

@celery_app.task(name="send_email_notification")
async def send_email_notification_task(
    email_to: str,
    subject: str,
    html_body: str,
    alert_name: Optional[str] = None, # For logging context
    trade_id: Optional[int] = None # For logging context
):
    """Celery task to send an email notification using SendGrid."""
    if not settings.email_api_key or not settings.email_from:
        logger.warning("Email configuration is missing. Skipping email notification.")
        return {"status": "skipped", "channel": "email", "error": "Email not configured"}

    try:
        payload = {
            "personalizations": [{"to": [{"email": email_to}]}],
            "from": {
                "email": settings.email_from,
                "name": settings.email_from_name,
            },
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}],
        }

        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client: # Using webhook timeout for emails too
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.email_api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status() # SendGrid returns 202 for success, but httpx.raise_for_status handles 2xx

        logger.info(f"Email sent successfully to {email_to} for alert '{alert_name or 'N/A'}' (trade_id={trade_id or 'N/A'}).")
        return {"status": "success", "channel": "email"}

    except httpx.HTTPStatusError as e:
        logger.error(f"SendGrid returned status {e.response.status_code}: {e.response.text[:200]}")
        return {"status": "error", "channel": "email", "error": str(e)}
    except httpx.RequestError as e:
        logger.error(f"SendGrid request failed: {str(e)[:200]}")
        return {"status": "error", "channel": "email", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending email to {email_to}: {str(e)[:200]}", exc_info=True)
        return {"status": "error", "channel": "email", "error": str(e)}


@celery_app.task(name="send_subscription_confirmation_email")
async def send_subscription_confirmation_email_task(
    email_to: str, tier: str, period_start_iso: str, period_end_iso: str
):
    """Celery task to send a subscription confirmation email."""
    if not settings.email_api_key or not settings.email_from:
        logger.warning("Email configuration is missing. Skipping subscription email.")
        return {"status": "skipped", "channel": "email", "error": "Email not configured"}

    tier_names = {"basic": "Basic", "pro": "Pro", "enterprise": "Enterprise"}
    tier_name = tier_names.get(tier.lower(), tier.capitalize())
    subject = f"🎉 Welcome to TradeSignal {tier_name}!"
    
    # Reconstruct datetime objects from ISO strings
    period_start = datetime.fromisoformat(period_start_iso)
    period_end = datetime.fromisoformat(period_end_iso)

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

    return await send_email_notification_task(email_to, subject, html_body, alert_name=f"Subscription {tier_name}")

@celery_app.task(name="send_test_email_notification")
async def send_test_email_notification_task(email_to: str, alert_name: str):
    """Celery task to send a test email notification."""
    if not settings.email_api_key or not settings.email_from:
        logger.warning("Email configuration is missing. Skipping test email.")
        return {"status": "skipped", "channel": "test_email", "error": "Email not configured"}

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
    return await send_email_notification_task(email_to, subject, html_body, alert_name=f"Test: {alert_name}")


@celery_app.task(name="send_push_notification")
async def send_push_notification_task(
    subscription_info: Dict[str, Any], # Must be serializable dict
    alert_name: str, # Using alert name for serialization
    trade_data: Dict[str, Any], # Using trade data for serialization
    company_name: str,
    insider_name: str,
    alert_id: Optional[int] = None # Assuming alert_id is passed
):
    """Celery task to send a browser push notification."""
    if not webpush:
        logger.warning("pywebpush not installed. Skipping push notification.")
        return {"status": "skipped", "channel": "push", "error": "pywebpush not installed"}

    if not settings.vapid_private_key or not settings.vapid_public_key:
        logger.warning("VAPID keys not configured. Skipping push notification.")
        return {"status": "skipped", "channel": "push", "error": "VAPID not configured"}

    try:
        trade_value = float(trade_data.get("total_value", 0))
        value_str = f"${trade_value:,.2f}"

        title = f"🔔 {alert_name}"
        body = (
            f"{insider_name} {trade_data.get('transaction_type').lower()}s {value_str} "
            f"of {trade_data.get('ticker')}"
        )

        payload = {
            "notification": {
                "title": title,
                "body": body,
                "icon": "/logo192.png",
                "badge": "/badge.png",
                "data": {
                    "url": f"/trades?ticker={trade_data.get('ticker')}",
                    "trade_id": trade_data.get('id'),
                    "alert_id": alert_id, 
                },
            }
        }

        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_subject},
        )

        logger.info(f"Push notification sent for alert '{alert_name}' (endpoint {subscription_info.get('endpoint')}).")
        return {"status": "success", "channel": "push"}

    except WebPushException as e:
        if hasattr(e, "response") and e.response.status_code == 410:
            logger.warning(f"Push subscription expired: {subscription_info.get('endpoint')}")
            return {"status": "expired", "channel": "push", "error": "Subscription expired (410 Gone)"}
        logger.error(f"Push failed for {subscription_info.get('endpoint')}: {str(e)[:200]}")
        return {"status": "error", "channel": "push", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending push to {subscription_info.get('endpoint')}: {str(e)[:200]}", exc_info=True)
        return {"status": "error", "channel": "push", "error": str(e)}

@celery_app.task(name="send_test_push_notification")
async def send_test_push_notification_task(subscription_info: Dict[str, Any], alert_name: str):
    """Celery task to send a test push notification."""
    if not webpush:
        logger.warning("pywebpush not installed. Skipping test push notification.")
        return {"status": "skipped", "channel": "test_push", "error": "pywebpush not installed"}

    if not settings.vapid_private_key or not settings.vapid_public_key:
        logger.warning("VAPID keys not configured. Skipping test push notification.")
        return {"status": "skipped", "channel": "test_push", "error": "VAPID not configured"}

    try:
        payload = {
            "notification": {
                "title": "✅ Test Notification",
                "body": f"Push notifications are working for {alert_name}!",
                "icon": "/logo192.png",
                "badge": "/badge.png",
                "data": {"url": "/alerts", "test": True},
            }
        }

        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_subject},
        )

        logger.info(f"Test push notification sent for alert '{alert_name}' (endpoint {subscription_info.get('endpoint')}).")
        return {"status": "success", "channel": "test_push"}

    except WebPushException as e:
        if hasattr(e, "response") and e.response.status_code == 410:
            logger.warning(f"Test push subscription expired: {subscription_info.get('endpoint')}")
            return {"status": "expired", "channel": "test_push", "error": "Subscription expired (410 Gone)"}
        logger.error(f"Test push failed for {subscription_info.get('endpoint')}: {str(e)[:200]}")
        return {"status": "error", "channel": "test_push", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending test push to {subscription_info.get('endpoint')}: {str(e)[:200]}", exc_info=True)
        return {"status": "error", "channel": "test_push", "error": str(e)}