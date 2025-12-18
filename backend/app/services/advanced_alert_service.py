"""
Advanced Alert Service.

Handles:
- Complex query evaluation (AND/OR/NOT)
- Visual query builder support
- Smart grouping
- ML recommendations
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from app.models.advanced_alert import (
    AdvancedAlertRule,
    AlertGroup,
    AlertTrigger,
    MLAlertRecommendation,
)
from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider

logger = logging.getLogger(__name__)


class AdvancedAlertService:
    """Service for advanced alert management and evaluation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alert_rule(
        self,
        user_id: int,
        name: str,
        query_structure: Dict[str, Any],
        notification_channels: List[str],
        description: Optional[str] = None,
        group_alerts: bool = False,
        group_window_minutes: int = 60,
        use_ml_recommendations: bool = False,
        ml_confidence_threshold: Optional[float] = None,
    ) -> AdvancedAlertRule:
        """Create a new advanced alert rule."""
        rule = AdvancedAlertRule(
            user_id=user_id,
            name=name,
            description=description,
            query_structure=query_structure,
            notification_channels=notification_channels,
            group_alerts=group_alerts,
            group_window_minutes=group_window_minutes,
            use_ml_recommendations=use_ml_recommendations,
            ml_confidence_threshold=ml_confidence_threshold,
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)

        return rule

    async def evaluate_alert_rule(
        self, rule_id: int, trade: Trade, company: Company, insider: Insider
    ) -> bool:
        """
        Evaluate if a trade matches an alert rule.

        Returns True if trade matches the rule's query structure.
        """
        rule = await self.db.get(AdvancedAlertRule, rule_id)
        if not rule or not rule.is_active:
            return False

        # Evaluate query structure
        matches = self._evaluate_query_structure(
            rule.query_structure, trade, company, insider
        )

        if matches:
            # Create trigger record
            trigger = AlertTrigger(
                rule_id=rule_id,
                trade_id=trade.id,
                matched_conditions=self._extract_matched_conditions(
                    rule.query_structure, trade, company, insider
                ),
            )

            # ML confidence if enabled
            if rule.use_ml_recommendations:
                trigger.ml_confidence = await self._calculate_ml_confidence(
                    rule, trade, company, insider
                )
                if (
                    rule.ml_confidence_threshold
                    and trigger.ml_confidence < rule.ml_confidence_threshold
                ):
                    return False  # Below confidence threshold

            # Handle grouping
            if rule.group_alerts:
                group = await self._get_or_create_alert_group(rule_id, trade, company)
                trigger.group_id = group.id
                group.trade_count += 1
            else:
                # Send immediately
                trigger.notification_sent = True
                trigger.notification_sent_at = datetime.utcnow()

            self.db.add(trigger)

            # Update rule stats
            rule.trigger_count += 1
            rule.last_triggered_at = datetime.utcnow()

            await self.db.commit()

        return matches

    def _evaluate_query_structure(
        self, query: Dict[str, Any], trade: Trade, company: Company, insider: Insider
    ) -> bool:
        """
        Evaluate query structure recursively.

        Supports AND, OR, NOT operators and nested conditions.
        """
        operator = query.get("operator", "AND")

        if operator == "NOT":
            condition = query.get("condition", {})
            return not self._evaluate_condition(condition, trade, company, insider)

        conditions = query.get("conditions", [])

        if operator == "AND":
            return all(
                self._evaluate_condition_or_group(c, trade, company, insider)
                for c in conditions
            )
        elif operator == "OR":
            return any(
                self._evaluate_condition_or_group(c, trade, company, insider)
                for c in conditions
            )

        return False

    def _evaluate_condition_or_group(
        self, condition: Dict[str, Any], trade: Trade, company: Company, insider: Insider
    ) -> bool:
        """Evaluate a condition or nested group."""
        if "operator" in condition:
            # Nested group
            return self._evaluate_query_structure(condition, trade, company, insider)
        else:
            # Simple condition
            return self._evaluate_condition(condition, trade, company, insider)

    def _evaluate_condition(
        self, condition: Dict[str, Any], trade: Trade, company: Company, insider: Insider
    ) -> bool:
        """Evaluate a single condition."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # Get field value
        field_value = self._get_field_value(field, trade, company, insider)

        # Apply operator
        if operator == "equals":
            return field_value == value
        elif operator == "not_equals":
            return field_value != value
        elif operator == "greater_than":
            return field_value > value
        elif operator == "less_than":
            return field_value < value
        elif operator == "greater_than_or_equal":
            return field_value >= value
        elif operator == "less_than_or_equal":
            return field_value <= value
        elif operator == "contains":
            return value in str(field_value).lower()
        elif operator == "in":
            return field_value in value if isinstance(value, list) else False
        elif operator == "not_in":
            return field_value not in value if isinstance(value, list) else True

        return False

    def _get_field_value(
        self, field: str, trade: Trade, company: Company, insider: Insider
    ) -> Any:
        """Get field value from trade, company, or insider."""
        field_map = {
            "ticker": company.ticker,
            "company_name": company.name,
            "trade_value": float(trade.total_value) if trade.total_value else 0.0,
            "shares": float(trade.shares) if trade.shares else 0.0,
            "transaction_type": trade.transaction_type,
            "insider_name": insider.name,
            "insider_role": insider.title or insider.relationship,
            "filing_date": trade.filing_date,
        }

        return field_map.get(field, None)

    def _extract_matched_conditions(
        self, query: Dict[str, Any], trade: Trade, company: Company, insider: Insider
    ) -> List[Dict[str, Any]]:
        """Extract which conditions matched."""
        matched = []

        conditions = query.get("conditions", [])
        for condition in conditions:
            if "operator" in condition:
                # Nested group
                nested_matched = self._extract_matched_conditions(
                    condition, trade, company, insider
                )
                if nested_matched:
                    matched.extend(nested_matched)
            else:
                # Simple condition
                if self._evaluate_condition(condition, trade, company, insider):
                    matched.append(condition)

        return matched

    async def _get_or_create_alert_group(
        self, rule_id: int, trade: Trade, company: Company
    ) -> AlertGroup:
        """Get or create an alert group for smart grouping."""
        # Generate group key (e.g., "AAPL-2024-01-15")
        group_key = f"{company.ticker}-{trade.filing_date.date()}"

        # Check for existing group within window
        rule = await self.db.get(AdvancedAlertRule, rule_id)
        window_start = datetime.utcnow() - timedelta(minutes=rule.group_window_minutes)

        result = await self.db.execute(
            select(AlertGroup).where(
                AlertGroup.rule_id == rule_id,
                AlertGroup.group_key == group_key,
                AlertGroup.expires_at > datetime.utcnow(),
                AlertGroup.is_sent.is_(False),
            )
        )
        group = result.scalar_one_or_none()

        if not group:
            # Create new group
            group = AlertGroup(
                rule_id=rule_id,
                group_key=group_key,
                expires_at=datetime.utcnow() + timedelta(minutes=rule.group_window_minutes),
            )
            self.db.add(group)
            await self.db.flush()

        return group

    async def _calculate_ml_confidence(
        self, rule: AdvancedAlertRule, trade: Trade, company: Company, insider: Insider
    ) -> float:
        """
        Calculate ML confidence score for alert trigger.

        Returns 0-100 confidence score.
        """
        # Simplified ML confidence calculation
        # In production, would use trained model
        confidence = 50.0  # Base confidence

        # Adjust based on factors
        if trade.total_value and trade.total_value > 1000000:
            confidence += 20  # Large trades are more significant

        if insider.title and any(
            role in insider.title.upper() for role in ["CEO", "CFO", "PRESIDENT"]
        ):
            confidence += 15  # C-suite trades are more significant

        if trade.transaction_type == "BUY":
            confidence += 10  # Buys are generally more significant

        return min(100.0, confidence)

    async def generate_ml_recommendations(self, user_id: int) -> List[MLAlertRecommendation]:
        """
        Generate ML-based alert recommendations for a user.

        Analyzes user behavior and suggests relevant alert rules.
        """
        # Simplified recommendation generation
        # In production, would use ML model trained on user behavior

        recommendations = []

        # Example: Recommend alert for frequently viewed tickers
        # (This would be replaced with actual ML model)

        recommendation = MLAlertRecommendation(
            user_id=user_id,
            suggested_rule_name="Large CEO Buys",
            suggested_query_structure={
                "operator": "AND",
                "conditions": [
                    {"field": "transaction_type", "operator": "equals", "value": "BUY"},
                    {"field": "insider_role", "operator": "contains", "value": "CEO"},
                    {"field": "trade_value", "operator": "greater_than", "value": 1000000},
                ],
            },
            reasoning="Based on your viewing patterns, you may be interested in large CEO purchases.",
            confidence_score=75.0,
            expected_trigger_frequency="weekly",
        )
        recommendations.append(recommendation)
        self.db.add(recommendation)

        await self.db.commit()

        return recommendations

