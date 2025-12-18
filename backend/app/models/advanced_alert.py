"""
Advanced Alert System models.

Visual query builder, complex logic (AND/OR/NOT), smart grouping, ML recommendations.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Index, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AdvancedAlertRule(Base):
    """
    Advanced alert rule with complex logic.

    Supports visual query builder with AND/OR/NOT operators.
    """

    __tablename__ = "advanced_alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Alert configuration
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Query builder structure (JSON)
    # Format: {
    #   "operator": "AND" | "OR",
    #   "conditions": [
    #     {"field": "ticker", "operator": "equals", "value": "AAPL"},
    #     {"field": "trade_value", "operator": "greater_than", "value": 1000000},
    #     {"operator": "NOT", "condition": {...}}
    #   ]
    # }
    query_structure: Mapped[str] = mapped_column(JSON, nullable=False)

    # Notification configuration
    notification_channels: Mapped[str] = mapped_column(JSON, nullable=False)  # ["email", "push", "webhook"]
    webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Smart grouping
    group_alerts: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    group_window_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # ML recommendations
    use_ml_recommendations: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ml_confidence_threshold: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # 0-100

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Statistics
    trigger_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<AdvancedAlertRule(id={self.id}, name={self.name}, user_id={self.user_id})>"


class AlertGroup(Base):
    """
    Alert group for smart grouping of related alerts.

    Groups multiple alert triggers together to reduce notification spam.
    """

    __tablename__ = "alert_groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("advanced_alert_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Group metadata
    group_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "AAPL-2024-01-15"
    trade_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<AlertGroup(id={self.id}, rule_id={self.rule_id}, group_key={self.group_key})>"


class AlertTrigger(Base):
    """
    Individual alert trigger record.

    Links trades to alert rules and groups.
    """

    __tablename__ = "alert_triggers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("advanced_alert_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("trades.id", ondelete="CASCADE"), nullable=False, index=True
    )
    group_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("alert_groups.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Trigger details
    matched_conditions: Mapped[str] = mapped_column(JSON, nullable=True)  # Which conditions matched
    ml_confidence: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # ML confidence score

    # Notification status
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notification_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_alert_triggers_rule_trade", "rule_id", "trade_id"),
        Index("ix_alert_triggers_group_triggered", "group_id", "triggered_at"),
    )

    def __repr__(self) -> str:
        return f"<AlertTrigger(id={self.id}, rule_id={self.rule_id}, trade_id={self.trade_id})>"


class MLAlertRecommendation(Base):
    """
    ML-generated alert recommendations.

    AI suggests alert rules based on user behavior and patterns.
    """

    __tablename__ = "ml_alert_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Recommendation details
    suggested_rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    suggested_query_structure: Mapped[str] = mapped_column(JSON, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)  # Why this recommendation

    # ML metrics
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100
    expected_trigger_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "daily", "weekly", etc.

    # Status
    is_accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # None = not reviewed
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<MLAlertRecommendation(id={self.id}, user_id={self.user_id}, "
            f"confidence={self.confidence_score})>"
        )

