"""
News Schemas

Pydantic models for news article data validation and serialization.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Individual news article schema."""

    id: int = Field(..., description="News article ID")
    headline: str = Field(..., description="Article headline")
    summary: str = Field(default="", description="Article summary")
    source: str = Field(..., description="News source")
    datetime: int = Field(
        ..., description="Unix timestamp of article publication"
    )  # noqa: A002
    url: str = Field(..., description="URL to full article")
    image: Optional[str] = Field(None, description="Article image URL")
    category: str = Field(default="general", description="News category")
    related: Optional[str] = Field(None, description="Comma-separated related tickers")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123456,
                "headline": "Market Rally Continues as Tech Stocks Soar",
                "summary": "Technology stocks led a broad market rally today...",
                "source": "Bloomberg",
                "datetime": 1704067200,
                "url": "https://example.com/article",
                "image": "https://example.com/image.jpg",
                "category": "general",
                "related": "AAPL,MSFT,GOOGL",
            }
        }


class NewsResponse(BaseModel):
    """Paginated news response."""

    articles: List[NewsArticle] = Field(..., description="List of news articles")
    total: int = Field(..., description="Total number of articles")
    limit: int = Field(..., description="Maximum articles returned")

    class Config:
        json_schema_extra = {"example": {"articles": [], "total": 50, "limit": 50}}


class NewsFilters(BaseModel):
    """Filter options for news queries."""

    category: Optional[str] = Field(
        None, description="News category (general, crypto, company)"
    )
    ticker: Optional[str] = Field(
        None, description="Company ticker for company-specific news"
    )
    days_back: Optional[int] = Field(
        7, ge=1, le=30, description="Number of days to look back"
    )
    limit: Optional[int] = Field(
        50, ge=1, le=100, description="Maximum articles to return"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "category": "general",
                "ticker": "AAPL",
                "days_back": 7,
                "limit": 50,
            }
        }
