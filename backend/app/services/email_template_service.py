"""
Email template service for managing default and custom email templates.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.marketing_campaign import EmailTemplate
from app.services.marketing_service import MarketingService

logger = logging.getLogger(__name__)


class EmailTemplateService:
    """Service for managing email templates."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.marketing_service = MarketingService(db)

    async def create_default_templates(self) -> Dict[str, EmailTemplate]:
        """Create default email templates for common use cases."""
        templates = {}

        # Welcome/Onboarding Template
        welcome_template = await self.marketing_service.create_email_template(
            name="welcome_email",
            subject="Welcome to TradeSignal - Start Tracking Insider Trades",
            html_body="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to TradeSignal!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {{ user_name }},</p>
                        <p>Thank you for joining TradeSignal! You now have access to real-time insider trading intelligence.</p>
                        <p><strong>Get started:</strong></p>
                        <ul>
                            <li>Track insider trades from SEC Form 4 filings</li>
                            <li>Monitor congressional trading activity</li>
                            <li>Set up alerts for companies you care about</li>
                            <li>Access AI-powered insights and analysis</li>
                        </ul>
                        <center>
                            <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
                        </center>
                        <p>Need help? Check out our <a href="{{ help_url }}">documentation</a> or reply to this email.</p>
                    </div>
                    <div class="footer">
                        <p>TradeSignal - Real-time Insider Trading Intelligence</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_body="""
            Welcome to TradeSignal!

            Hi {{ user_name }},

            Thank you for joining TradeSignal! You now have access to real-time insider trading intelligence.

            Get started:
            - Track insider trades from SEC Form 4 filings
            - Monitor congressional trading activity
            - Set up alerts for companies you care about
            - Access AI-powered insights and analysis

            Go to Dashboard: {{ dashboard_url }}

            Need help? Check out our documentation: {{ help_url }}

            TradeSignal - Real-time Insider Trading Intelligence
            """,
        )
        templates["welcome"] = welcome_template

        # Upgrade Prompt Template
        upgrade_template = await self.marketing_service.create_email_template(
            name="upgrade_prompt",
            subject="Unlock Premium Features - Upgrade to TradeSignal Pro",
            html_body="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .feature-list { list-style: none; padding: 0; }
                    .feature-list li { padding: 10px 0; border-bottom: 1px solid #ddd; }
                    .feature-list li:before { content: "✓ "; color: #4CAF50; font-weight: bold; }
                    .button { display: inline-block; padding: 12px 30px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Unlock Premium Features</h1>
                    </div>
                    <div class="content">
                        <p>Hi {{ user_name }},</p>
                        <p>You've been using TradeSignal's free tier. Upgrade to <strong>TradeSignal Pro</strong> to unlock:</p>
                        <ul class="feature-list">
                            <li>Unlimited company tracking</li>
                            <li>Advanced AI insights (100 requests/month)</li>
                            <li>Real-time trade alerts</li>
                            <li>Intrinsic Value Targets (IVT)</li>
                            <li>Risk Level assessments</li>
                            <li>TradeSignal Scores</li>
                            <li>API access</li>
                        </ul>
                        <center>
                            <a href="{{ upgrade_url }}" class="button">Upgrade Now - $99/month</a>
                        </center>
                        <p><small>Special offer: Use code <strong>UPGRADE20</strong> for 20% off your first month!</small></p>
                    </div>
                    <div class="footer">
                        <p>TradeSignal - Real-time Insider Trading Intelligence</p>
                    </div>
                </div>
            </body>
            </html>
            """,
        )
        templates["upgrade"] = upgrade_template

        # Re-engagement Template
        reengagement_template = await self.marketing_service.create_email_template(
            name="re_engagement",
            subject="We Miss You - Check Out What's New at TradeSignal",
            html_body="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; padding: 12px 30px; background: #4facfe; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>We Miss You!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {{ user_name }},</p>
                        <p>It's been a while since you last visited TradeSignal. We've added some exciting new features:</p>
                        <ul>
                            <li><strong>AI-Powered Daily Summaries</strong> - Get insights on the day's most significant trades</li>
                            <li><strong>Intrinsic Value Targets</strong> - DCF-based stock valuations</li>
                            <li><strong>TradeSignal Scores</strong> - Comprehensive stock ratings</li>
                            <li><strong>Portfolio Analysis</strong> - Track your virtual portfolios</li>
                        </ul>
                        <center>
                            <a href="{{ dashboard_url }}" class="button">Explore New Features</a>
                        </center>
                        <p>See what you've been missing!</p>
                    </div>
                    <div class="footer">
                        <p>TradeSignal - Real-time Insider Trading Intelligence</p>
                    </div>
                </div>
            </body>
            </html>
            """,
        )
        templates["re_engagement"] = reengagement_template

        logger.info(f"Created {len(templates)} default email templates")
        return templates

    async def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get a template by name."""
        return await self.marketing_service.get_template_by_name(name)

    async def render_template(
        self, template_name: str, variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """Render a template with variables."""
        template = await self.get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        subject = self._render_string(template.subject, variables)
        html_body = self._render_string(template.html_body, variables)
        text_body = (
            self._render_string(template.text_body, variables)
            if template.text_body
            else None
        )

        return {
            "subject": subject,
            "html_body": html_body,
            "text_body": text_body,
        }

    def _render_string(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template string with variables."""
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
        return rendered

