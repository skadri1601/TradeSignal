"""
News API Router

Endpoints for market news articles from Finnhub News API.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.news_service import NewsService
from app.models.user import User
from app.core.security import get_current_active_user
from app.schemas.news import NewsResponse, NewsArticle

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["News"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get("/general", response_model=NewsResponse)
@limiter.limit("30/minute")
async def get_general_news(
    request: Request,
    limit: int = Query(50, ge=1, le=100, description="Maximum articles to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get general market news.

    Returns:
        List of general market news articles
    """
    try:
        service = NewsService(db)
        articles = await service.get_general_news(limit=limit)

        # Convert to NewsArticle schema
        news_articles = [
            NewsArticle(
                id=article.get("id", idx),
                headline=article.get("headline", ""),
                summary=article.get("summary", ""),
                source=article.get("source", ""),
                datetime=article.get("datetime", 0),
                url=article.get("url", ""),
                image=article.get("image"),
                category="general",
                related=article.get("related"),
            )
            for idx, article in enumerate(articles)
        ]

        return NewsResponse(
            articles=news_articles, total=len(news_articles), limit=limit
        )
    except Exception as e:
        logger.error(f"Error in get_general_news endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch general news. Please try again later.",
        )


@router.get("/company/{ticker}", response_model=NewsResponse)
@limiter.limit("30/minute")
async def get_company_news(
    request: Request,
    ticker: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum articles to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get company-specific news.

    Args:
        ticker: Company ticker symbol

    Returns:
        List of news articles for the company
    """
    try:
        service = NewsService(db)
        articles = await service.get_company_news(ticker=ticker, limit=limit)

        # Convert to NewsArticle schema
        news_articles = [
            NewsArticle(
                id=article.get("id", idx),
                headline=article.get("headline", ""),
                summary=article.get("summary", ""),
                source=article.get("source", ""),
                datetime=article.get("datetime", 0),
                url=article.get("url", ""),
                image=article.get("image"),
                category="company",
                related=ticker,
            )
            for idx, article in enumerate(articles)
        ]

        return NewsResponse(
            articles=news_articles, total=len(news_articles), limit=limit
        )
    except Exception as e:
        logger.error(
            f"Error in get_company_news endpoint for {ticker}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch news for {ticker}. Please try again later.",
        )


@router.get("/crypto", response_model=NewsResponse)
@limiter.limit("30/minute")
async def get_crypto_news(
    request: Request,
    limit: int = Query(50, ge=1, le=100, description="Maximum articles to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get crypto news.

    Returns:
        List of crypto news articles
    """
    try:
        service = NewsService(db)
        articles = await service.get_crypto_news(limit=limit)

        # Convert to NewsArticle schema
        news_articles = [
            NewsArticle(
                id=article.get("id", idx),
                headline=article.get("headline", ""),
                summary=article.get("summary", ""),
                source=article.get("source", ""),
                datetime=article.get("datetime", 0),
                url=article.get("url", ""),
                image=article.get("image"),
                category="crypto",
                related=article.get("related"),
            )
            for idx, article in enumerate(articles)
        ]

        return NewsResponse(
            articles=news_articles, total=len(news_articles), limit=limit
        )
    except Exception as e:
        logger.error(f"Error in get_crypto_news endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch crypto news. Please try again later.",
        )


@router.get("/latest", response_model=NewsResponse)
@limiter.limit("30/minute")
async def get_latest_news(
    request: Request,
    limit: int = Query(50, ge=1, le=100, description="Maximum articles to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get latest news from all categories (general, company, crypto).

    Returns:
        Combined list of latest news articles from all categories
    """
    try:
        service = NewsService(db)
        articles = await service.get_latest_news(limit=limit)

        # Convert to NewsArticle schema
        news_articles = [
            NewsArticle(
                id=article.get("id", idx),
                headline=article.get("headline", ""),
                summary=article.get("summary", ""),
                source=article.get("source", ""),
                datetime=article.get("datetime", 0),
                url=article.get("url", ""),
                image=article.get("image"),
                category=article.get("category", "general"),
                related=article.get("related"),
            )
            for idx, article in enumerate(articles)
        ]

        return NewsResponse(
            articles=news_articles, total=len(news_articles), limit=limit
        )
    except Exception as e:
        logger.error(f"Error in get_latest_news endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest news. Please try again later.",
        )
