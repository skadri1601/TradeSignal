"""
Marketing campaign models for email automation, drip campaigns, and conversion tracking.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum

from app.database import Base


class CampaignType(str, Enum):
    """Types of marketing campaigns."""
    DRIP = "drip"  # Automated email sequences
    PROMOTIONAL = "promotional"  # One-off promotional emails
    ONBOARDING = "onboarding"  # Welcome series
    RE_ENGAGEMENT = "re_engagement"  # Win-back campaigns
    UPSELL = "upsell"  # Upgrade prompts


class CampaignStatus(str, Enum):
    """Campaign status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class EmailTemplate(Base):
    """
    Email template for marketing campaigns.

    Attributes:
        id: Primary key
        name: Template name
        subject: Email subject line
        html_body: HTML email body
        text_body: Plain text version
        variables: JSON of template variables
        created_at: When template was created
        updated_at: When template was last updated
    """

    __tablename__ = "email_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    html_body: Mapped[str] = mapped_column(Text, nullable=False)
    text_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Template variables
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class MarketingCampaign(Base):
    """
    Marketing campaign for email automation.

    Attributes:
        id: Primary key
        name: Campaign name
        campaign_type: Type of campaign
        status: Campaign status
        template_id: Email template to use
        target_segment: User segment criteria (JSON)
        schedule: Campaign schedule (JSON)
        created_at: When campaign was created
        updated_at: When campaign was last updated
    """

    __tablename__ = "marketing_campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign_type: Mapped[str] = mapped_column(
        SQLEnum(CampaignType), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT, index=True
    )
    template_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("email_templates.id"), nullable=True
    )
    target_segment: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # User segment criteria
    schedule: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Schedule configuration
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    template: Mapped["EmailTemplate | None"] = relationship("EmailTemplate")


class CampaignEmail(Base):
    """
    Individual email sent as part of a campaign.

    Attributes:
        id: Primary key
        campaign_id: Foreign key to MarketingCampaign
        user_id: Foreign key to User
        template_id: Email template used
        subject: Email subject
        sent_at: When email was sent
        opened_at: When email was opened (if tracked)
        clicked_at: When link was clicked (if tracked)
        bounced: Whether email bounced
        unsubscribed: Whether user unsubscribed
    """

    __tablename__ = "campaign_emails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("marketing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    template_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("email_templates.id"), nullable=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    bounced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unsubscribed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ConversionEvent(Base):
    """
    Track conversion events for marketing attribution.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        event_type: Type of conversion (signup, upgrade, purchase, etc.)
        campaign_id: Associated campaign (if any)
        source: Traffic source (organic, paid, referral, etc.)
        medium: Marketing medium (email, social, search, etc.)
        referrer: Referrer URL
        conversion_value: Value of conversion (if applicable)
        created_at: When conversion occurred
    """

    __tablename__ = "conversion_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    campaign_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("marketing_campaigns.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    medium: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    referrer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    conversion_value: Mapped[float | None] = mapped_column(Integer, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Additional event data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

