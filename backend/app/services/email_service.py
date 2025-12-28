"""
Email Service for sending transactional emails.

Supports multiple email providers:
- Resend (default)
- SendGrid
- Brevo (formerly Sendinblue)

Emails are sent directly (synchronously) - Celery tasks removed.
"""

import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def _send_email_direct(
    email_to: str,
    subject: str,
    html_body: str,
) -> Dict[str, Any]:
    """
    Send email directly using configured provider (synchronous, no Celery).
    
    Returns:
        Dict with status and details
    """
    if not settings.email_api_key or not settings.email_from:
        logger.warning("Email configuration missing. Cannot send email.")
        return {"status": "skipped", "error": "Email configuration missing"}
    
    email_service = getattr(settings, 'email_service', 'resend')
    
    try:
        if email_service == 'resend':
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.email_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.email_from,
                        "to": [email_to],
                        "subject": subject,
                        "html": html_body,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    logger.info(f"Email sent successfully to {email_to}")
                    return {"status": "sent", "provider": "resend"}
                else:
                    logger.error(f"Resend error: {response.status_code} - {response.text}")
                    return {"status": "error", "error": response.text}
        else:
            # Other providers can be added here
            logger.warning(f"Email provider '{email_service}' not implemented for direct send")
            return {"status": "skipped", "error": f"Provider {email_service} not implemented"}
            
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


class EmailService:
    """Service for sending transactional emails."""

    @staticmethod
    def _build_password_reset_html(reset_url: str, expires_hours: int = 1) -> str:
        """Build HTML email template for password reset."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password - TradeSignal</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 10px;
        }}
        h1 {{
            color: #1f2937;
            font-size: 24px;
            margin: 0 0 20px 0;
        }}
        p {{
            color: #4b5563;
            font-size: 16px;
            margin: 0 0 15px 0;
        }}
        .button {{
            display: inline-block;
            padding: 14px 28px;
            background-color: #2563eb;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
            text-align: center;
        }}
        .button:hover {{
            background-color: #1d4ed8;
        }}
        .reset-link {{
            word-break: break-all;
            color: #2563eb;
            text-decoration: none;
            background-color: #eff6ff;
            padding: 12px;
            border-radius: 4px;
            display: block;
            margin: 20px 0;
            font-family: monospace;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
        .warning {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning-text {{
            color: #92400e;
            font-size: 14px;
            margin: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">TradeSignal</div>
        </div>
        <h1>Reset Your Password</h1>
        <p>We received a request to reset your password for your TradeSignal account.</p>
        <p>Click the button below to reset your password. This link will expire in {expires_hours} hour(s).</p>
        
        <center>
            <a href="{reset_url}" class="button">Reset Password</a>
        </center>
        
        <p>Or copy and paste this link into your browser:</p>
        <a href="{reset_url}" class="reset-link">{reset_url}</a>
        
        <div class="warning">
            <p class="warning-text">
                <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, 
                please ignore this email. Your password will remain unchanged.
            </p>
        </div>
        
        <div class="footer">
            <p>This is an automated message from TradeSignal.</p>
            <p>If you have any questions, please contact our support team.</p>
        </div>
    </div>
</body>
</html>
        """

    @staticmethod
    async def send_password_reset_email(
        email: str, reset_token: str, expires_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Send password reset email to user.

        Args:
            email: User's email address
            reset_token: Password reset token
            expires_hours: Hours until token expires (default: 1)

        Returns:
            Dict with status and task_id if enqueued
        """
        if not settings.email_api_key or not settings.email_from:
            logger.warning(
                "Email configuration missing. Cannot send password reset email."
            )
            return {
                "status": "skipped",
                "error": "Email configuration missing",
            }

        # Build reset URL (frontend expects token as URL param, not query param)
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
        reset_url = f"{frontend_url}/reset-password/{reset_token}"

        # Build email content
        subject = "Reset Your TradeSignal Password"
        html_body = EmailService._build_password_reset_html(reset_url, expires_hours)

        # Send email directly (no Celery)
        try:
            result = await _send_email_direct(
                email_to=email,
                subject=subject,
                html_body=html_body,
            )
            if result.get("status") == "sent":
                logger.info(f"Password reset email sent to {email}")
            return result
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

    @staticmethod
    async def send_welcome_email(email: str, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Send welcome email to new user.

        Args:
            email: User's email address
            user_name: Optional user name for personalization

        Returns:
            Dict with status and task_id if enqueued
        """
        if not settings.email_api_key or not settings.email_from:
            logger.warning("Email configuration missing. Cannot send welcome email.")
            return {
                "status": "skipped",
                "error": "Email configuration missing",
            }

        name = user_name or "there"
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
        subject = "Welcome to TradeSignal - Thank You for Choosing Us!"
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to TradeSignal</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: #7c3aed;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }}
        h1 {{
            color: #1f2937;
            font-size: 26px;
            margin: 0 0 20px 0;
            text-align: center;
        }}
        p {{
            color: #4b5563;
            font-size: 16px;
            margin: 0 0 15px 0;
        }}
        .highlight {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }}
        .button {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 25px 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
            transition: transform 0.2s;
        }}
        .button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }}
        .features {{
            background-color: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
        }}
        .features h2 {{
            color: #1f2937;
            font-size: 18px;
            margin: 0 0 15px 0;
        }}
        .features ul {{
            margin: 0;
            padding-left: 20px;
            color: #4b5563;
        }}
        .features li {{
            margin: 8px 0;
            font-size: 15px;
        }}
        .footer {{
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .support-link {{
            color: #7c3aed;
            text-decoration: none;
        }}
        .support-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">TradeSignal.</div>
        </div>
        <h1>Welcome, {name}!</h1>
        <p>Thank you for choosing <span class="highlight">TradeSignal</span>! We're thrilled to have you join our community of informed traders and investors.</p>
        
        <p>At TradeSignal, we provide you with <strong>real-time insider trading intelligence</strong> to help you make smarter investment decisions. You now have access to:</p>
        
        <div class="features">
            <h2>🚀 What You Can Do:</h2>
            <ul>
                <li><strong>Track Insider Trades</strong> - Monitor SEC Form 4 filings and congressional trades in real-time</li>
                <li><strong>AI-Powered Insights</strong> - Get intelligent analysis of market-moving transactions</li>
                <li><strong>Custom Alerts</strong> - Set up personalized notifications for trades that matter to you</li>
                <li><strong>Market Analysis</strong> - Explore comprehensive data on companies, insiders, and trading patterns</li>
                <li><strong>Congressional Trading</strong> - Follow what politicians are buying and selling</li>
            </ul>
        </div>
        
        <p>Ready to get started? Click the button below to explore your dashboard and begin discovering investment opportunities.</p>
        
        <center>
            <a href="{frontend_url}/dashboard" class="button">Get Started →</a>
        </center>
        
        <p style="margin-top: 25px; font-size: 15px;">If you have any questions or need assistance, our support team is here to help. Don't hesitate to reach out!</p>
        
        <div class="footer">
            <p><strong>Happy Trading!</strong></p>
            <p>The TradeSignal Team</p>
            <p style="margin-top: 15px;">
                <a href="{frontend_url}/support" class="support-link">Contact Support</a> | 
                <a href="{frontend_url}" class="support-link">Visit Website</a>
            </p>
        </div>
    </div>
</body>
</html>
        """

        # Send email directly (no Celery)
        try:
            result = await _send_email_direct(
                email_to=email,
                subject=subject,
                html_body=html_body,
            )
            if result.get("status") == "sent":
                logger.info(f"Welcome email sent to {email}")
            return result
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

