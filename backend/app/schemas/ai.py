"""
Pydantic schemas for AI endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CompanyAnalysisResponse(BaseModel):
    """Response for company analysis endpoint."""

    ticker: str
    company_name: str
    days_analyzed: int
    total_trades: int
    analysis: str
    sentiment: str
    insights: List[str]
    timestamp: str
    provider: Optional[str] = Field(None, description="AI provider that generated the analysis")
    error: Optional[str] = None


class TopTrade(BaseModel):
    """Individual top trade."""

    ticker: str
    company: str
    insider: str
    role: str
    type: str
    shares: float
    value: float
    date: str


class CompanySummary(BaseModel):
    """Individual company summary in news feed."""

    ticker: str
    company_name: str
    summary: str
    total_value: float
    trade_count: int
    buy_count: int
    sell_count: int
    insider_count: int
    latest_date: str


class DailySummaryResponse(BaseModel):
    """Response for daily summary endpoint."""

    company_summaries: List[CompanySummary]
    total_trades: int
    generated_at: str
    period: str
    error: Optional[str] = None


class ChatQuestion(BaseModel):
    """Request for chatbot endpoint."""

    question: str = Field(
        ..., min_length=1, max_length=500, description="User's question"
    )


class ChatResponse(BaseModel):
    """Response for chatbot endpoint."""

    question: str
    answer: str
    timestamp: str
    error: Optional[str] = None
    response_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata about response quality (truncation, safety filters, etc.)"
    )


class TradingSignal(BaseModel):
    """Individual trading signal."""

    ticker: str
    company_name: str
    signal: str  # BULLISH, BEARISH, NEUTRAL
    strength: str  # STRONG, MODERATE, WEAK
    trade_count: int
    buy_volume: int
    sell_volume: int
    buy_ratio: float  # Percentage


class TradingSignalsResponse(BaseModel):
    """Response for trading signals endpoint."""

    signals: List[TradingSignal]
    generated_at: str
    period: str
    message: Optional[str] = None
    error: Optional[str] = None
