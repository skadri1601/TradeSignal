"""
Pricing API Router.

Endpoints for subscription tiers, pricing, and upgrade flows.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subscription import SubscriptionTier, TIER_LIMITS
from app.services.tier_service import TierService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.get("/tiers")
async def get_pricing_tiers(
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get all available subscription tiers with pricing and features.

    Public endpoint (authentication optional).
    """
    tiers = []

    for tier_enum in SubscriptionTier:
        tier = tier_enum.value
        limits = TIER_LIMITS.get(tier, {})

        # Pricing information
        pricing = {
            "free": {"monthly": 0, "yearly": 0},
            "basic": {"monthly": 0, "yearly": 0},  # Legacy tier
            "plus": {"monthly": 29, "yearly": 290},  # $29/mo
            "pro": {"monthly": 99, "yearly": 990},  # $99/mo (Research Pro)
            "enterprise": {"monthly": 499, "yearly": 4990},  # $499/mo
        }.get(tier, {"monthly": 0, "yearly": 0})

        tier_info = {
            "tier": tier,
            "name": tier.replace("_", " ").title(),
            "pricing": pricing,
            "features": {
                "ai_requests_limit": limits.get("ai_requests_limit", 0),
                "alerts_max": limits.get("alerts_max", 0),
                "real_time_updates": limits.get("real_time_updates", False),
                "api_access": limits.get("api_access", False),
                "research_api": limits.get("research_api", False),
                "companies_tracked": limits.get("companies_tracked", 0),
                "historical_data_days": limits.get("historical_data_days", 0),
                "export_enabled": limits.get("export_enabled", False),
                "advanced_screening": limits.get("advanced_screening", False),
                "priority_support": limits.get("priority_support", False),
            },
        }

        # Add Research Pro specific features
        if tier == SubscriptionTier.PRO.value:
            tier_info["features"].update({
                "intrinsic_value_targets": True,
                "risk_levels": True,
                "tradesignal_scores": True,
                "advanced_analytics": True,
            })

        # Add Enterprise specific features
        if tier == SubscriptionTier.ENTERPRISE.value:
            tier_info["features"].update({
                "intrinsic_value_targets": True,
                "risk_levels": True,
                "management_scores": True,
                "competitive_strength": True,
                "tradesignal_scores": True,
                "advanced_analytics": True,
                "custom_integrations": True,
                "dedicated_support": True,
            })

        tiers.append(tier_info)

    # Get current user's tier if authenticated
    current_tier = None
    if current_user:
        current_tier = await TierService.get_user_tier(current_user.id, db)

    return {
        "tiers": tiers,
        "current_tier": current_tier,
    }


@router.get("/tiers/{tier}/features")
async def get_tier_features(
    tier: str,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get detailed features for a specific tier.

    Public endpoint (authentication optional).
    """
    tier_lower = tier.lower()
    if tier_lower not in [t.value for t in SubscriptionTier]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {tier}"
        )

    limits = TIER_LIMITS.get(tier_lower, TIER_LIMITS[SubscriptionTier.FREE.value])

    features = {
        "tier": tier_lower,
        "limits": limits,
        "feature_list": [
            {
                "name": "AI Insights",
                "enabled": limits.get("ai_requests_limit", 0) > 0,
                "limit": limits.get("ai_requests_limit", 0),
                "description": "AI-powered trade analysis and insights",
            },
            {
                "name": "Alerts",
                "enabled": limits.get("alerts_max", 0) > 0,
                "limit": limits.get("alerts_max", 0),
                "description": "Real-time trade alerts",
            },
            {
                "name": "Real-time Updates",
                "enabled": limits.get("real_time_updates", False),
                "description": "Real-time data updates",
            },
            {
                "name": "API Access",
                "enabled": limits.get("api_access", False),
                "description": "Programmatic API access",
            },
            {
                "name": "Research API",
                "enabled": limits.get("research_api", False),
                "description": "Access to research features (IVT, Risk Levels, Scores)",
            },
            {
                "name": "Company Tracking",
                "enabled": True,
                "limit": limits.get("companies_tracked", 0),
                "description": "Number of companies you can track",
            },
            {
                "name": "Historical Data",
                "enabled": limits.get("historical_data_days", 0) > 0,
                "limit": limits.get("historical_data_days", 0),
                "description": "Days of historical data access",
            },
            {
                "name": "Data Export",
                "enabled": limits.get("export_enabled", False),
                "description": "Export data to CSV/Excel",
            },
            {
                "name": "Advanced Screening",
                "enabled": limits.get("advanced_screening", False),
                "description": "Advanced stock screening tools",
            },
        ],
    }

    # Add Research Pro features
    if tier_lower == SubscriptionTier.PRO.value:
        features["feature_list"].extend([
            {
                "name": "Intrinsic Value Targets",
                "enabled": True,
                "description": "DCF-based stock valuations",
            },
            {
                "name": "Risk Level Assessments",
                "enabled": True,
                "description": "Comprehensive risk analysis",
            },
            {
                "name": "TradeSignal Scores",
                "enabled": True,
                "description": "Overall stock ratings",
            },
        ])

    # Add Enterprise features
    if tier_lower == SubscriptionTier.ENTERPRISE.value:
        features["feature_list"].extend([
            {
                "name": "Management Scores",
                "enabled": True,
                "description": "Management excellence ratings",
            },
            {
                "name": "Competitive Strength",
                "enabled": True,
                "description": "Competitive advantage analysis",
            },
            {
                "name": "Custom Integrations",
                "enabled": True,
                "description": "Custom API integrations",
            },
            {
                "name": "Dedicated Support",
                "enabled": True,
                "description": "Priority customer support",
            },
        ])

    return features


@router.get("/comparison")
async def get_pricing_comparison(
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get side-by-side pricing comparison for all tiers.

    Public endpoint (authentication optional).
    """
    tiers_data = await get_pricing_tiers(current_user, db)
    
    # Format for comparison table
    comparison = {
        "features": [
            "AI Insights",
            "Alerts",
            "Real-time Updates",
            "API Access",
            "Research API",
            "Company Tracking",
            "Historical Data",
            "Data Export",
            "Advanced Screening",
            "Intrinsic Value Targets",
            "Risk Levels",
            "Management Scores",
            "Competitive Strength",
            "TradeSignal Scores",
            "Priority Support",
        ],
        "tiers": [],
    }

    for tier_info in tiers_data["tiers"]:
        tier = tier_info["tier"]
        features = tier_info["features"]
        
        tier_comparison = {
            "tier": tier,
            "name": tier_info["name"],
            "pricing": tier_info["pricing"],
            "feature_values": {
                "AI Insights": f"{features['ai_requests_limit']}/month" if features.get("ai_requests_limit", 0) > 0 else "Limited",
                "Alerts": f"{features['alerts_max']}" if features.get("alerts_max", 0) > 0 else "Limited",
                "Real-time Updates": "✓" if features.get("real_time_updates") else "✗",
                "API Access": "✓" if features.get("api_access") else "✗",
                "Research API": "✓" if features.get("research_api") else "✗",
                "Company Tracking": "Unlimited" if features.get("companies_tracked") == -1 else str(features.get("companies_tracked", 0)),
                "Historical Data": "Unlimited" if features.get("historical_data_days") == -1 else f"{features.get('historical_data_days', 0)} days",
                "Data Export": "✓" if features.get("export_enabled") else "✗",
                "Advanced Screening": "✓" if features.get("advanced_screening") else "✗",
                "Intrinsic Value Targets": "✓" if tier in [SubscriptionTier.PRO.value, SubscriptionTier.ENTERPRISE.value] else "✗",
                "Risk Levels": "✓" if tier in [SubscriptionTier.PRO.value, SubscriptionTier.ENTERPRISE.value] else "✗",
                "Management Scores": "✓" if tier == SubscriptionTier.ENTERPRISE.value else "✗",
                "Competitive Strength": "✓" if tier == SubscriptionTier.ENTERPRISE.value else "✗",
                "TradeSignal Scores": "✓" if tier in [SubscriptionTier.PRO.value, SubscriptionTier.ENTERPRISE.value] else "✗",
                "Priority Support": "✓" if features.get("priority_support") else "✗",
            },
        }
        comparison["tiers"].append(tier_comparison)

    return {
        "comparison": comparison,
        "current_tier": tiers_data.get("current_tier"),
    }

