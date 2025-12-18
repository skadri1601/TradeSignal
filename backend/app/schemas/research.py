"""
Pydantic schemas for Research API responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IVTResponse(BaseModel):
    """Intrinsic Value Target response schema."""
    ticker: str
    intrinsic_value: float = Field(..., description="Calculated intrinsic value per share")
    current_price: float = Field(..., description="Current stock price")
    discount_premium_pct: float = Field(..., description="Discount/premium percentage (positive = discount)")
    wacc: float = Field(..., description="Weighted Average Cost of Capital")
    terminal_growth_rate: float = Field(..., description="Terminal growth rate assumption")
    calculated_at: datetime = Field(..., description="When IVT was calculated")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "intrinsic_value": 185.50,
                "current_price": 175.20,
                "discount_premium_pct": 5.88,
                "wacc": 0.085,
                "terminal_growth_rate": 0.025,
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }


class RiskLevelResponse(BaseModel):
    """Risk Level assessment response schema."""
    ticker: str
    risk_level: str = Field(..., description="Risk level (Very Low, Low, Moderate, High, Very High)")
    score: float = Field(..., description="Risk score (0-100)")
    component_scores: Dict[str, float] = Field(..., description="Individual component scores")
    calculated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "risk_level": "Low",
                "score": 25.5,
                "component_scores": {
                    "earnings_volatility": 20.0,
                    "financial_leverage": 15.0,
                    "operating_leverage": 30.0,
                    "concentration": 25.0,
                    "industry_stability": 35.0
                },
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }


class ManagementScoreResponse(BaseModel):
    """Management Score response schema."""
    ticker: str
    grade: str = Field(..., description="Management grade (A, B, C, D, F)")
    composite_score: float = Field(..., description="Composite management score")
    component_scores: Dict[str, float] = Field(..., description="Individual component scores")
    calculated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "grade": "A",
                "composite_score": 85.5,
                "component_scores": {
                    "m_and_a": 80.0,
                    "capital_discipline": 90.0,
                    "shareholder_returns": 85.0,
                    "leverage_management": 88.0,
                    "governance": 84.0
                },
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }


class CompetitiveStrengthResponse(BaseModel):
    """Competitive Strength rating response schema."""
    ticker: str
    rating: str = Field(..., description="Rating (Dominant, Strong, Moderate, Weak, None)")
    composite_score: float = Field(..., description="Composite competitive strength score")
    component_scores: Dict[str, float] = Field(..., description="Individual component scores")
    trajectory: str = Field(..., description="Trajectory (Improving, Stable, Declining)")
    calculated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "rating": "Dominant",
                "composite_score": 92.5,
                "component_scores": {
                    "network_effects": 95.0,
                    "intangible_assets": 90.0,
                    "cost_advantages": 88.0,
                    "switching_costs": 95.0,
                    "efficient_scale": 94.0
                },
                "trajectory": "Stable",
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }


class TSScoreResponse(BaseModel):
    """TradeSignal Score response schema."""
    ticker: str
    ts_score: float = Field(..., description="TradeSignal Score (0-100)")
    badge: str = Field(..., description="Score badge (Excellent, Strong, Good, Moderate, Weak, Poor)")
    components: Dict[str, float] = Field(..., description="Component scores")
    calculated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "ts_score": 85.5,
                "badge": "Excellent",
                "components": {
                    "insider_buy_ratio": 0.75,
                    "ivt_discount_premium": 5.88,
                    "risk_score": 25.5,
                    "politician_score": 0.80
                },
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }


class ComprehensiveResearchResponse(BaseModel):
    """Comprehensive research data response schema."""
    ticker: str
    ivt: Optional[Dict[str, Optional[float]]] = Field(None, description="Intrinsic Value Target data")
    risk_level: Optional[Dict[str, Any]] = Field(None, description="Risk level assessment")
    ts_score: Optional[Dict[str, Any]] = Field(None, description="TradeSignal Score")
    management_score: Optional[Dict[str, Any]] = Field(None, description="Management score (Enterprise only)")
    competitive_strength: Optional[Dict[str, Any]] = Field(None, description="Competitive strength (Enterprise only)")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "ivt": {
                    "intrinsic_value": 185.50,
                    "current_price": 175.20,
                    "discount_premium_pct": 5.88
                },
                "risk_level": {
                    "risk_level": "Low",
                    "score": 25.5
                },
                "ts_score": {
                    "score": 85.5,
                    "badge": "Excellent"
                },
                "management_score": {
                    "grade": "A",
                    "composite_score": 85.5
                },
                "competitive_strength": {
                    "rating": "Dominant",
                    "composite_score": 92.5,
                    "trajectory": "Stable"
                }
            }
        }

