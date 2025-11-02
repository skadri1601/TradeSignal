"""
Configuration management for TradeSignal API.

Uses Pydantic Settings v2 for type-safe environment variable loading.
Validates required fields and provides sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Required fields will raise validation errors if not provided.
    """

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string",
        alias="DATABASE_URL"
    )

    # Security & Authentication
    jwt_secret: str = Field(
        ...,
        description="Secret key for JWT signing",
        alias="JWT_SECRET"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
        alias="JWT_ALGORITHM"
    )
    jwt_expiration_hours: int = Field(
        default=24,
        description="JWT token expiration in hours",
        alias="JWT_EXPIRATION_HOURS"
    )

    # External API Keys (Optional for now)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI insights",
        alias="OPENAI_API_KEY"
    )
    alpha_vantage_api_key: Optional[str] = Field(
        default=None,
        description="Alpha Vantage API key for market data",
        alias="ALPHA_VANTAGE_API_KEY"
    )
    coingecko_api_key: Optional[str] = Field(
        default=None,
        description="CoinGecko API key for crypto data",
        alias="COINGECKO_API_KEY"
    )

    # SEC EDGAR Configuration (Required)
    sec_user_agent: str = Field(
        ...,
        description="SEC EDGAR API user agent (format: 'Name email@example.com')",
        alias="SEC_USER_AGENT"
    )

    scraper_timezone: str = Field(
        default="UTC",
        description="Timezone for the scraper",
        alias="SCRAPER_TIMEZONE"
    )

    significant_trade_threshold: int = Field(
        default=100000,
        description="Threshold for significant trades in USD",
        alias="SIGNIFICANT_TRADE_THRESHOLD"
    )

    # Alert & Notification Configuration
    alerts_enabled: bool = Field(
        default=True,
        description="Enable alert system",
        alias="ALERTS_ENABLED"
    )
    alert_check_interval_minutes: int = Field(
        default=5,
        description="How often to check for alert triggers (minutes)",
        alias="ALERT_CHECK_INTERVAL_MINUTES"
    )
    max_alerts_per_user: int = Field(
        default=50,
        description="Maximum alerts per user",
        alias="MAX_ALERTS_PER_USER"
    )
    alert_cooldown_minutes: int = Field(
        default=60,
        description="Minimum minutes between notifications for same alert/trade combo",
        alias="ALERT_COOLDOWN_MINUTES"
    )
    webhook_timeout_seconds: int = Field(
        default=10,
        description="Webhook request timeout",
        alias="WEBHOOK_TIMEOUT_SECONDS"
    )
    webhook_retry_count: int = Field(
        default=3,
        description="Number of webhook retry attempts",
        alias="WEBHOOK_RETRY_COUNT"
    )

    # Feature Flags
    enable_ai_insights: bool = Field(
        default=False,
        description="Enable AI-powered trade insights",
        alias="ENABLE_AI_INSIGHTS"
    )
    enable_webhooks: bool = Field(
        default=False,
        description="Enable webhook notifications",
        alias="ENABLE_WEBHOOKS"
    )
    enable_email_alerts: bool = Field(
        default=False,
        description="Enable email alert notifications",
        alias="ENABLE_EMAIL_ALERTS"
    )

    # Redis Configuration (Optional)
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL for caching",
        alias="REDIS_URL"
    )

    # Application Configuration
    environment: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
        alias="ENVIRONMENT"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode",
        alias="DEBUG"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        alias="LOG_LEVEL"
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175",
        description="Comma-separated list of allowed CORS origins",
        alias="CORS_ORIGINS"
    )

    # API Configuration
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API version 1 route prefix"
    )
    project_name: str = Field(
        default="TradeSignal API",
        description="Project name for API documentation"
    )
    project_version: str = Field(
        default="1.0.0",
        description="API version"
    )

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
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

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of: {', '.join(valid_levels)}"
            )
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is a known environment."""
        valid_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(
                f"ENVIRONMENT must be one of: {', '.join(valid_envs)}"
            )
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
        """
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url_async(self) -> str:
        """
        Get async database URL for SQLAlchemy.

        Supports both asyncpg and psycopg drivers.
        Converts postgresql:// to postgresql+asyncpg:// by default.
        """
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url
        elif self.database_url.startswith("postgresql+psycopg://"):
            return self.database_url
        else:
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://', 'postgresql+asyncpg://', or 'postgresql+psycopg://'"
            )


# Global settings instance
# Import this in other modules: from app.config import settings
settings = Settings()
