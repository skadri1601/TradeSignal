"""
Configuration management for TradeSignal API.

Uses Pydantic Settings v2 for type-safe environment variable loading.
Validates required fields and provides sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Force load .env file with override BEFORE pydantic-settings loads
# This ensures .env values take precedence over any existing environment variables
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file, override=True)
_env_local = Path(__file__).parent.parent / ".env.local"
if _env_local.exists():
    load_dotenv(_env_local, override=True)

from pydantic_settings import BaseSettings, SettingsConfigDict  # noqa: E402
from pydantic import Field, field_validator  # noqa: E402
from typing import Optional  # noqa: E402


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Required fields will raise validation errors if not provided.
    """

    # Database Configuration
    database_url: str = Field(
        ..., description="PostgreSQL connection string", alias="DATABASE_URL"
    )

    # Security & Authentication
    jwt_secret: str = Field(
        ..., description="Secret key for JWT signing", alias="JWT_SECRET"
    )
    jwt_algorithm: str = Field(
        default="HS256", description="JWT signing algorithm", alias="JWT_ALGORITHM"
    )
    jwt_expiration_hours: int = Field(
        default=4,
        description="JWT token expiration in hours",
        alias="JWT_EXPIRATION_HOURS",
    )

    # External API Keys (Optional for now)
    # AI Provider Selection
    ai_provider: str = Field(
        default="gemini",
        description="AI provider to use (gemini, openai)",
        alias="AI_PROVIDER",
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI insights",
        alias="OPENAI_API_KEY",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use (gpt-4o-mini, gpt-4o, gpt-4-turbo)",
        alias="OPENAI_MODEL",
    )

    # Gemini Configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for AI insights",
        alias="GEMINI_API_KEY",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model to use (e.g., gemini-2.5-flash, gemini-2.0-flash)",
        alias="GEMINI_MODEL",
    )
    gemini_reasoning_model: str = Field(
        default="gemini-2.5-flash",
        description="Model for LUNA deep analysis (using Flash for cost efficiency)",
        alias="GEMINI_REASONING_MODEL",
    )

    # Shared AI Settings
    ai_max_tokens: int = Field(
        default=1000,
        description="Maximum tokens for AI responses",
        alias="AI_MAX_TOKENS",
    )
    ai_temperature: float = Field(
        default=0.7,
        description="AI temperature for response creativity (0-2)",
        alias="AI_TEMPERATURE",
    )
    ai_cache_ttl_hours: int = Field(
        default=24,
        description="Hours to cache AI responses",
        alias="AI_CACHE_TTL_HOURS",
    )
    alpha_vantage_api_key: Optional[str] = Field(
        default=None,
        description="Alpha Vantage API key for market data",
        alias="ALPHA_VANTAGE_API_KEY",
    )
    finnhub_api_key: Optional[str] = Field(
        default=None,
        description="Finnhub API key for market data (FREE tier: 60 calls/min)",
        alias="FINNHUB_API_KEY",
    )
    coingecko_api_key: Optional[str] = Field(
        default=None,
        description="CoinGecko API key for crypto data",
        alias="COINGECKO_API_KEY",
    )
    financial_modeling_prep_api_key: Optional[str] = Field(
        default=None,
        description="Financial Modeling Prep API key for company financials (IVT calculation)",
        alias="FINANCIAL_MODELING_PREP_API_KEY",
    )

    # Federal Reserve Data (FRED API)
    fred_api_key: Optional[str] = Field(
        default=None,
        description="FRED API key for Federal Reserve data (free from https://fred.stlouisfed.org)",
        alias="FRED_API_KEY",
    )

    # Multi-Channel Alerts
    discord_webhook_url: Optional[str] = Field(
        default=None,
        description="Discord webhook URL for alerts",
        alias="DISCORD_WEBHOOK_URL",
    )
    slack_webhook_url: Optional[str] = Field(
        default=None,
        description="Slack webhook URL for alerts",
        alias="SLACK_WEBHOOK_URL",
    )
    twilio_account_sid: Optional[str] = Field(
        default=None,
        description="Twilio Account SID for SMS alerts",
        alias="TWILIO_ACCOUNT_SID",
    )
    twilio_auth_token: Optional[str] = Field(
        default=None,
        description="Twilio Auth Token for SMS alerts",
        alias="TWILIO_AUTH_TOKEN",
    )
    twilio_phone_number: Optional[str] = Field(
        default=None,
        description="Twilio phone number for SMS alerts",
        alias="TWILIO_PHONE_NUMBER",
    )

    # SEC EDGAR Configuration (Required)
    sec_user_agent: str = Field(
        ...,
        description="SEC EDGAR API user agent (format: 'Name email@example.com')",
        alias="SEC_USER_AGENT",
    )
    sec_api_timeout_seconds: int = Field(
        default=60,
        description="SEC API request timeout in seconds (default: 60)",
        alias="SEC_API_TIMEOUT_SECONDS",
    )
    sec_api_max_retries: int = Field(
        default=3,
        description="Maximum number of retries for SEC API requests on timeout (default: 3)",
        alias="SEC_API_MAX_RETRIES",
    )

    # AI Insights Configuration
    ai_insights_days_back: int = Field(
        default=7,
        description="Number of days to look back for AI insights (Daily Summary, Trading Signals)",
        alias="AI_INSIGHTS_DAYS_BACK",
    )

    significant_trade_threshold: int = Field(
        default=100000,
        description="Threshold for significant trades in USD",
        alias="SIGNIFICANT_TRADE_THRESHOLD",
    )

    scraper_timezone: str = Field(
        default="America/Chicago",
        description="Timezone for the scraper (CDT - Dallas, TX)",
        alias="SCRAPER_TIMEZONE",
    )

    # Scheduler Configuration (Phase 4)
    scheduler_enabled: bool = Field(
        default=True,
        description="Enable automated periodic scraping",
        alias="SCHEDULER_ENABLED",
    )
    scraper_schedule_hours: str = Field(
        default="0,6,12,18",
        description="Hours to run scraper (comma-separated, 24-hour format)",
        alias="SCRAPER_SCHEDULE_HOURS",
    )
    scraper_days_back: int = Field(
        default=7,
        description="Days to look back when scraping",
        alias="SCRAPER_DAYS_BACK",
    )
    scraper_max_filings: int = Field(
        default=10,
        description="Maximum filings to process per company",
        alias="SCRAPER_MAX_FILINGS",
    )
    scraper_cooldown_hours: int = Field(
        default=4,
        description="Hours to wait before re-scraping same company",
        alias="SCRAPER_COOLDOWN_HOURS",
    )
    scraper_max_companies_per_run: int = Field(
        default=100,
        description="Maximum number of companies to process per scraper run",
        alias="SCRAPER_MAX_COMPANIES_PER_RUN",
    )
    scraper_priority_recent_days: int = Field(
        default=7,
        description="Days threshold for highest priority queue (recent filings)",
        alias="SCRAPER_PRIORITY_RECENT_DAYS",
    )
    scraper_priority_medium_days: int = Field(
        default=30,
        description="Days threshold for medium priority queue",
        alias="SCRAPER_PRIORITY_MEDIUM_DAYS",
    )
    
    # Batch processing configuration
    batch_processing_max_tickers_per_run: int = Field(
        default=100,
        description="Maximum tickers to process per batch run",
        alias="BATCH_PROCESSING_MAX_TICKERS_PER_RUN",
    )
    batch_processing_batch_size: int = Field(
        default=10,
        description="Number of tickers to process in each batch",
        alias="BATCH_PROCESSING_BATCH_SIZE",
    )
    batch_processing_rate_limit_delay: float = Field(
        default=1.0,
        description="Seconds to wait between API calls for rate limiting",
        alias="BATCH_PROCESSING_RATE_LIMIT_DELAY",
    )
    
    # Popular tickers configuration
    popular_tickers_count: int = Field(
        default=100,
        description="Number of popular tickers to pre-calculate",
        alias="POPULAR_TICKERS_COUNT",
    )
    popular_tickers_source: str = Field(
        default="market_cap",
        description="Source for popular tickers: market_cap, trade_volume, user_watchlists",
        alias="POPULAR_TICKERS_SOURCE",
    )
    
    # Cache TTLs
    cache_competitive_strength_ttl: int = Field(
        default=86400,
        description="Cache TTL for competitive strength scores in seconds (24 hours)",
        alias="CACHE_COMPETITIVE_STRENGTH_TTL",
    )
    cache_management_score_ttl: int = Field(
        default=86400,
        description="Cache TTL for management scores in seconds (24 hours)",
        alias="CACHE_MANAGEMENT_SCORE_TTL",
    )

    # Congressional Trading Configuration (Phase 7)
    congressional_scraper_enabled: bool = Field(
        default=True,
        description="Enable automated congressional trade scraping",
        alias="CONGRESSIONAL_SCRAPER_ENABLED",
    )
    congressional_scrape_hours: str = Field(
        default="0,6,12,18",
        description="Hours to run congressional scraper (comma-separated, every 6 hours)",
        alias="CONGRESSIONAL_SCRAPE_HOURS",
    )
    congressional_scrape_days_back: int = Field(
        default=60,
        description="Days to look back for congressional trades (45-day filing window + buffer)",
        alias="CONGRESSIONAL_SCRAPE_DAYS_BACK",
    )
    congressional_rate_limit: int = Field(
        default=50,
        description="Congressional API rate limit (requests per minute)",
        alias="CONGRESSIONAL_RATE_LIMIT",
    )
    congressional_cache_ttl_hours: int = Field(
        default=6,
        description="Hours to cache congressional trade data",
        alias="CONGRESSIONAL_CACHE_TTL_HOURS",
    )
    use_fallback_sources: bool = Field(
        default=True,
        description="Whether to use fallback sources for congressional data if Finnhub fails",
        alias="USE_FALLBACK_SOURCES",
    )
    congressional_fallback_max_age_days: int = Field(
        default=7,
        description="Maximum age in days for fallback congressional trade data to be considered fresh",
        alias="CONGRESSIONAL_FALLBACK_MAX_AGE_DAYS",
    )

    # Alert & Notification Configuration
    alerts_enabled: bool = Field(
        default=True, description="Enable alert system", alias="ALERTS_ENABLED"
    )
    alert_check_interval_minutes: int = Field(
        default=5,
        description="How often to check for alert triggers (minutes)",
        alias="ALERT_CHECK_INTERVAL_MINUTES",
    )
    max_alerts_per_user: int = Field(
        default=50, description="Maximum alerts per user", alias="MAX_ALERTS_PER_USER"
    )
    alert_cooldown_minutes: int = Field(
        default=60,
        description="Minimum minutes between notifications for same alert/trade combo",
        alias="ALERT_COOLDOWN_MINUTES",
    )
    webhook_timeout_seconds: int = Field(
        default=10,
        description="Webhook request timeout",
        alias="WEBHOOK_TIMEOUT_SECONDS",
    )
    webhook_retry_count: int = Field(
        default=3,
        description="Number of webhook retry attempts",
        alias="WEBHOOK_RETRY_COUNT",
    )

    # Email Configuration (Phase 5B)
    email_service: str = Field(
        default="resend",
        description="Email service to use (resend, brevo, sendgrid)",
        alias="EMAIL_SERVICE",
    )
    email_api_key: Optional[str] = Field(
        default=None, description="API key for the email service", alias="EMAIL_API_KEY"
    )
    email_from: Optional[str] = Field(
        default_factory=lambda: os.environ.get("EMAIL_FROM", None),
        description="Email address to send from",
        alias="EMAIL_FROM",
    )
    email_from_name: str = Field(
        default_factory=lambda: os.environ.get("EMAIL_FROM_NAME", "TradeSignal Alerts"),
        description="Name to send emails from",
        alias="EMAIL_FROM_NAME",
    )

    # Push Notification Configuration (Phase 5C)
    vapid_private_key: Optional[str] = Field(
        default=None,
        description="VAPID private key for Web Push (PEM format)",
        alias="VAPID_PRIVATE_KEY",
    )
    vapid_public_key: Optional[str] = Field(
        default=None,
        description="VAPID public key for Web Push (PEM format)",
        alias="VAPID_PUBLIC_KEY",
    )
    vapid_public_key_base64: Optional[str] = Field(
        default=None,
        description="VAPID public key in URL-safe base64 for frontend",
        alias="VAPID_PUBLIC_KEY_BASE64",
    )
    vapid_subject: Optional[str] = Field(
        default=None,
        description="VAPID subject (mailto: or https: URL)",
        alias="VAPID_SUBJECT",
    )

    # OAuth & Encryption
    token_encryption_key: str = Field(
        default="",
        description="Fernet encryption key for OAuth tokens (generate with: openssl rand -base64 32)",
        alias="TOKEN_ENCRYPTION_KEY",
    )

    # Alpaca Broker Configuration
    alpaca_oauth_client_id: str = Field(
        default="",
        description="Alpaca OAuth client ID",
        alias="ALPACA_OAUTH_CLIENT_ID",
    )
    alpaca_oauth_client_secret: str = Field(
        default="",
        description="Alpaca OAuth client secret",
        alias="ALPACA_OAUTH_CLIENT_SECRET",
    )
    alpaca_redirect_uri: str = Field(
        default="https://api.tradesignal.capital/api/v1/brokerage/callback/alpaca",
        description="Alpaca OAuth redirect URI (use HTTPS in production)",
        alias="ALPACA_REDIRECT_URI",
    )

    # TD Ameritrade Broker Configuration
    td_ameritrade_client_id: str = Field(
        default="",
        description="TD Ameritrade OAuth client ID",
        alias="TD_AMERITRADE_CLIENT_ID",
    )
    td_ameritrade_redirect_uri: str = Field(
        default="https://api.tradesignal.capital/api/v1/brokerage/callback/td_ameritrade",
        description="TD Ameritrade OAuth redirect URI (use HTTPS in production)",
        alias="TD_AMERITRADE_REDIRECT_URI",
    )

    # Interactive Brokers Configuration
    ib_client_id: str = Field(
        default="",
        description="Interactive Brokers OAuth client ID",
        alias="IB_CLIENT_ID",
    )
    ib_redirect_uri: str = Field(
        default="https://api.tradesignal.capital/api/v1/brokerage/callback/ib",
        description="Interactive Brokers OAuth redirect URI (use HTTPS in production)",
        alias="IB_REDIRECT_URI",
    )

    # Feature Flags
    enable_ai_insights: bool = Field(
        default=False,
        description="Enable AI-powered trade insights",
        alias="ENABLE_AI_INSIGHTS",
    )
    enable_webhooks: bool = Field(
        default=False,
        description="Enable webhook notifications",
        alias="ENABLE_WEBHOOKS",
    )
    enable_email_alerts: bool = Field(
        default=False,
        description="Enable email alert notifications",
        alias="ENABLE_EMAIL_ALERTS",
    )
    enable_push_notifications: bool = Field(
        default=False,
        description="Enable browser push notifications",
        alias="ENABLE_PUSH_NOTIFICATIONS",
    )

    # LUNA AI Enhancement - Market Data Features
    enable_technical_analysis: bool = Field(
        default=False,
        description="Enable technical analysis features (charts, RSI, MACD, moving averages)",
        alias="ENABLE_TECHNICAL_ANALYSIS",
    )
    enable_fundamental_analysis: bool = Field(
        default=False,
        description="Enable fundamental analysis features (P/E, financials, ratios)",
        alias="ENABLE_FUNDAMENTAL_ANALYSIS",
    )
    enable_news_sentiment: bool = Field(
        default=False,
        description="Enable news sentiment analysis (requires Finnhub API)",
        alias="ENABLE_NEWS_SENTIMENT",
    )
    enable_analyst_ratings: bool = Field(
        default=False,
        description="Enable analyst ratings and price targets (requires Finnhub API)",
        alias="ENABLE_ANALYST_RATINGS",
    )

    # LUNA AI Enhancement - Price Prediction Features
    enable_price_predictions: bool = Field(
        default=False,
        description="Enable AI-powered price predictions with timeframes",
        alias="ENABLE_PRICE_PREDICTIONS",
    )
    prediction_timeframes: str = Field(
        default="1week,1month,3months,6months",
        description="Comma-separated prediction timeframes",
        alias="PREDICTION_TIMEFRAMES",
    )
    price_prediction_disclaimer: str = Field(
        default="This analysis is for educational and informational purposes only. It does not constitute investment advice. Past performance is not indicative of future results. Always consult with a licensed financial advisor before making investment decisions.",
        description="Legal disclaimer for price predictions",
        alias="PRICE_PREDICTION_DISCLAIMER",
    )

    # Market Data Sources
    yfinance_enabled: bool = Field(
        default=True,
        description="Enable yfinance for market data (technical indicators, fundamentals)",
        alias="YFINANCE_ENABLED",
    )
    newsapi_key: Optional[str] = Field(
        default=None,
        description="NewsAPI key for news sentiment analysis (optional)",
        alias="NEWSAPI_KEY",
    )

    # Proxy & Load Balancer Configuration
    trust_proxy_headers: bool = Field(
        default=True,
        description="Trust X-Forwarded-Proto and other proxy headers (required for Render, Heroku, etc.)",
        alias="TRUST_PROXY_HEADERS",
    )

    # Clerk Auth Configuration
    clerk_secret_key: Optional[str] = Field(
        default=None,
        description="Clerk secret key for backend JWT verification",
        alias="CLERK_SECRET_KEY",
    )
    clerk_publishable_key: Optional[str] = Field(
        default=None,
        description="Clerk publishable key",
        alias="CLERK_PUBLISHABLE_KEY",
    )
    clerk_webhook_secret: Optional[str] = Field(
        default=None,
        description="Clerk webhook signing secret (from Clerk Dashboard > Webhooks)",
        alias="CLERK_WEBHOOK_SECRET",
    )

    # Supabase Auth Configuration (Gradual Migration)
    supabase_url: Optional[str] = Field(
        default=None,
        description="Supabase project URL",
        alias="SUPABASE_URL",
    )
    supabase_anon_key: Optional[str] = Field(
        default=None,
        description="Supabase anon/public key (safe for frontend)",
        alias="SUPABASE_ANON_KEY",
    )
    supabase_service_role_key: Optional[str] = Field(
        default=None,
        description="Supabase service role key (backend only, keep secret!)",
        alias="SUPABASE_SERVICE_ROLE_KEY",
    )

    # Redis Configuration (Phase 4.1 - Caching)
    redis_url: Optional[str] = Field(
        default=None, description="Redis connection URL for caching", alias="REDIS_URL"
    )
    redis_host: str = Field(
        default="127.0.0.1", description="Redis host", alias="REDIS_HOST"
    )
    redis_port: int = Field(default=6379, description="Redis port", alias="REDIS_PORT")

    # Application Configuration
    environment: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
        alias="ENVIRONMENT",
    )
    debug: bool = Field(default=False, description="Enable debug mode (disabled by default for security)", alias="DEBUG")
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        alias="LOG_LEVEL",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="https://tradesignal.capital,https://www.tradesignal.capital",
        description="Comma-separated list of allowed CORS origins (use HTTPS in production)",
        alias="CORS_ORIGINS",
    )

    # API Configuration
    api_v1_prefix: str = Field(
        default="/api/v1", description="API version 1 route prefix"
    )
    project_name: str = Field(
        default="TradeSignal API", description="Project name for API documentation"
    )
    project_version: str = Field(default="1.0.0", description="API version")

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    @field_validator("sec_user_agent")
    @classmethod
    def validate_sec_user_agent(cls, v: str) -> str:
        """
        Validate SEC user agent format.

        SEC requires user agent in format: "Name email@example.com"
        """
        if not v or len(v.strip()) < 10:
            raise ValueError(
                "SEC_USER_AGENT must be in format: 'YourName your@email.com'. "
                "This is required by SEC EDGAR API."
            )
        if "@" not in v:
            raise ValueError(
                "SEC_USER_AGENT must include an email address. "
                "Format: 'YourName your@email.com'"
            )
        return v.strip()

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """
        Validate JWT secret is strong enough.

        Requires at least 32 characters for security.
        Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
        """
        if not v or len(v) < 32:
            raise ValueError(
                "JWT_SECRET must be at least 32 characters for security. "
                'Generate a strong secret with: python -c "import secrets; print(secrets.token_urlsafe(64))"'
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is a known environment."""
        valid_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(valid_envs)}")
        return v_lower

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Get CORS origins as a list.

        Converts comma-separated string to list of origins.
        Automatically includes localhost origins in development mode.
        """
        origins = [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]
        
        # Auto-include localhost origins in development mode
        if self.is_development:
            localhost_origins = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
                "http://127.0.0.1:8080",
            ]
            # Add localhost origins that aren't already in the list
            for localhost_origin in localhost_origins:
                if localhost_origin not in origins:
                    origins.append(localhost_origin)
        
        return origins

    @property
    def database_url_async(self) -> str:
        """
        Get async database URL for SQLAlchemy.

        Supports both asyncpg and psycopg drivers.
        Converts postgresql:// to postgresql+asyncpg:// by default.
        Force Port 5432 for Supabase to avoid Transaction Mode (PgBouncer) issues.
        """
        url = self.database_url
        
        # FIX: Force Port 5432 for Supabase connections to bypass Transaction Mode pooler
        # Transaction Mode (6543) breaks SQLAlchemy/asyncpg prepared statements
        if "supabase.com" in url or "supabase.co" in url:
            if ":6543" in url:
                url = url.replace(":6543", ":5432")
        
        if url.startswith("postgresql://"):
            return url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        elif url.startswith("postgresql+asyncpg://"):
            return url
        elif url.startswith("postgresql+psycopg://"):
            return url
        else:
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://', 'postgresql+asyncpg://', or 'postgresql+psycopg://'"
            )

    # Auth properties for compatibility with security.py
    @property
    def secret_key(self) -> str:
        """Alias for jwt_secret for compatibility."""
        return self.jwt_secret

    @property
    def algorithm(self) -> str:
        """Alias for jwt_algorithm for compatibility."""
        return self.jwt_algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes (converted from hours)."""
        return self.jwt_expiration_hours * 60

    @property
    def refresh_token_expire_days(self) -> int:
        """Get refresh token expiration in days."""
        return 30  # Default to 30 days for refresh tokens

    @property
    def prediction_timeframes_list(self) -> list[str]:
        """
        Get prediction timeframes as a list.

        Converts comma-separated string to list of timeframes.
        """
        return [
            timeframe.strip()
            for timeframe in self.prediction_timeframes.split(",")
            if timeframe.strip()
        ]


# Global settings instance
# Import this in other modules: from app.config import settings
settings = Settings()
