"""
SQLAlchemy models for TradeSignal.

Import all models here for easy access and to ensure they're registered
with SQLAlchemy metadata.
"""

from app.models.company import Company
from app.models.insider import Insider
from app.models.trade import Trade, TransactionType, TransactionCode
from app.models.congressperson import Congressperson, Chamber, Party
from app.models.congressional_trade import CongressionalTrade, OwnerType
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.models.scrape_job import ScrapeJob
from app.models.scrape_history import ScrapeHistory
from app.models.push_subscription import PushSubscription
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.models.usage import UsageTracking
from app.models.feature_usage_log import FeatureUsageLog
from app.models.risk_level import RiskLevelAssessment, RiskLevel
from app.models.tradesignal_score import TradeSignalScore
from app.models.intrinsic_value import IntrinsicValueTarget
from app.models.management_score import ManagementScore, ManagementGrade
from app.models.competitive_strength import CompetitiveStrengthRating, CompetitiveStrength
from app.models.organization import (
    Organization,
    OrganizationMember,
    OrganizationInvite,
    OrganizationRole,
    AuditLog,
)
from app.models.institutional_holding import (
    InstitutionalHolding,
    InstitutionalPositionChange,
)
from app.models.lobbying_activity import (
    LobbyingActivity,
    CompanyPoliticianRelationship,
)
from app.models.forum import (
    ForumTopic,
    ForumPost,
    ForumComment,
    ForumVote,
    ForumModerationLog,
)
from app.models.api_key import (
    UserAPIKey,
    APIKeyUsage,
)
from app.models.portfolio import (
    VirtualPortfolio,
    PortfolioPosition,
    PortfolioTransaction,
    PortfolioPerformance,
)
from app.models.thesis import (
    Thesis,
    ThesisTag,
    ThesisTagAssociation,
    ThesisImage,
    ThesisVote,
    ThesisComment,
    UserReputation,
)
from app.models.advanced_alert import (
    AdvancedAlertRule,
    AlertGroup,
    AlertTrigger,
    MLAlertRecommendation,
)
from app.models.analytics import (
    AnalyticsEvent,
    FunnelStep,
    FunnelAnalysis,
    ExecutiveDashboard,
    DataWarehouseETL,
)
from app.models.brokerage import (
    BrokerageAccount,
    CopyTradeRule,
    ExecutedTrade,
)
from app.models.user import User
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.job import Job
from app.models.job_application import JobApplication, ApplicationStatus
from app.models.contact_submission import ContactSubmission
from app.models.notification import Notification
from app.models.processed_filing import ProcessedFiling
from app.models.marketing_campaign import (
    EmailTemplate,
    MarketingCampaign,
    CampaignEmail,
    ConversionEvent,
    CampaignType,
    CampaignStatus,
)
from app.models.webhook import (
    WebhookEndpoint,
    WebhookDelivery,
    WebhookEventType,
    WebhookStatus,
)
from app.models.market_data import (
    DividendHistory,
    EarningsCalendar,
    AnalystRecommendation,
    FinancialStatement,
    PriceTarget,
    EarningsSurprise,
)

__all__ = [
    "Company",
    "Insider",
    "Trade",
    "TransactionType",
    "TransactionCode",
    "Congressperson",
    "Chamber",
    "Party",
    "CongressionalTrade",
    "OwnerType",
    "Alert",
    "AlertHistory",
    "ScrapeJob",
    "ScrapeHistory",
    "PushSubscription",
    "Subscription",
    "SubscriptionTier",
    "SubscriptionStatus",
    "UsageTracking",
    "FeatureUsageLog",
    "RiskLevelAssessment",
    "RiskLevel",
    "TradeSignalScore",
    "IntrinsicValueTarget",
    "ManagementScore",
    "ManagementGrade",
    "CompetitiveStrengthRating",
    "CompetitiveStrength",
    "Organization",
    "OrganizationMember",
    "OrganizationInvite",
    "OrganizationRole",
    "AuditLog",
    "InstitutionalHolding",
    "InstitutionalPositionChange",
    "LobbyingActivity",
    "CompanyPoliticianRelationship",
    "ForumTopic",
    "ForumPost",
    "ForumComment",
    "ForumVote",
    "ForumModerationLog",
    "VirtualPortfolio",
    "PortfolioPosition",
    "PortfolioTransaction",
    "PortfolioPerformance",
    "Thesis",
    "ThesisTag",
    "ThesisTagAssociation",
    "ThesisImage",
    "ThesisVote",
    "ThesisComment",
    "UserReputation",
    "AdvancedAlertRule",
    "AlertGroup",
    "AlertTrigger",
    "MLAlertRecommendation",
    "AnalyticsEvent",
    "FunnelStep",
    "FunnelAnalysis",
    "ExecutiveDashboard",
    "DataWarehouseETL",
    "BrokerageAccount",
    "CopyTradeRule",
    "ExecutedTrade",
    "User",
    "Payment",
    "PaymentStatus",
    "PaymentType",
    "Job",
    "JobApplication",
    "ApplicationStatus",
    "ContactSubmission",
    "Notification",
    "ProcessedFiling",
    "EmailTemplate",
    "MarketingCampaign",
    "CampaignEmail",
    "ConversionEvent",
    "CampaignType",
    "CampaignStatus",
    "WebhookEndpoint",
    "WebhookDelivery",
    "WebhookEventType",
    "WebhookStatus",
    "UserAPIKey",
    "APIKeyUsage",
    "DividendHistory",
    "EarningsCalendar",
    "AnalystRecommendation",
    "FinancialStatement",
    "PriceTarget",
    "EarningsSurprise",
]
