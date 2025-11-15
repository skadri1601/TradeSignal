"""
Stock Price API Router

Endpoints for fetching live stock prices from Yahoo Finance.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.stock_price_service import StockPriceService
from app.services.market_status_service import MarketStatusService
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/stocks", tags=["stocks"])

# Initialize limiter for this router
limiter = Limiter(key_func=get_remote_address)


class StockQuote(BaseModel):
    """Stock quote response model."""
    ticker: str
    company_name: Optional[str] = None
    current_price: float
    previous_close: float
    price_change: float
    price_change_percent: float
    market_cap: Optional[int] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    market_state: str
    updated_at: str


class PriceHistoryPoint(BaseModel):
    """Single price history data point."""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("/quote/{ticker}", response_model=StockQuote)
@limiter.limit("30/minute")
async def get_stock_quote(request: Request, ticker: str):
    """
    Get current stock quote for a ticker.

    Rate Limit: 30 requests per minute per IP

    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)

    Returns:
        Current stock price and market data

    Example:
        GET /api/v1/stocks/quote/TSLA
    """
    quote = StockPriceService.get_stock_quote(ticker.upper())

    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch quote for ticker {ticker}"
        )

    return quote


@router.get("/quotes", response_model=List[StockQuote])
@limiter.limit("10/minute")
async def get_multiple_quotes(
    request: Request,
    tickers: str = Query(..., description="Comma-separated list of ticker symbols")
):
    """
    Get quotes for multiple tickers.

    Rate Limit: 10 requests per minute per IP

    Args:
        tickers: Comma-separated ticker symbols (e.g., "TSLA,AAPL,GOOGL")

    Returns:
        List of stock quotes

    Example:
        GET /api/v1/stocks/quotes?tickers=TSLA,AAPL,GOOGL
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]

    if len(ticker_list) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 tickers allowed per request"
        )

    quotes_dict = StockPriceService.get_multiple_quotes(ticker_list)

    # Filter out failed quotes and return successful ones
    quotes = [q for q in quotes_dict.values() if q is not None]

    return quotes


@router.get("/market-overview", response_model=List[StockQuote])
@limiter.limit("10/minute")
async def get_market_overview(
    request: Request,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(None, ge=1, description="Number of companies to return (default: all)")
):
    """
    Get live market data for companies with recent insider trading activity.

    Rate Limit: 10 requests per minute per IP

    This endpoint fetches current stock prices for companies that have had
    insider trades in the last 30 days, sorted by most active.

    Args:
        limit: Maximum number of companies to return (default: all companies in database)

    Returns:
        List of stock quotes with insider trading activity

    Example:
        GET /api/v1/stocks/market-overview
        GET /api/v1/stocks/market-overview?limit=50
    """
    quotes = await StockPriceService.get_quotes_for_active_companies(db, limit=limit)

    # Return empty list instead of 404 if no quotes available
    return quotes if quotes else []


@router.get("/history/{ticker}", response_model=List[PriceHistoryPoint])
@limiter.limit("20/minute")
async def get_price_history(
    request: Request,
    ticker: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history")
):
    """
    Get historical price data for a ticker.

    Rate Limit: 20 requests per minute per IP

    Args:
        ticker: Stock ticker symbol
        days: Number of days of historical data (1-365)

    Returns:
        List of historical price data points

    Example:
        GET /api/v1/stocks/history/TSLA?days=30
    """
    history = StockPriceService.get_price_history(ticker.upper(), days=days)

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch price history for ticker {ticker}"
        )

    return history


@router.get("/market/status")
@limiter.limit("60/minute")
async def get_market_status(request: Request):
    """
    Get current US market status (open/closed).

    Uses pandas-market-calendars to accurately detect:
    - Regular trading hours (9:30 AM - 4:00 PM ET)
    - Weekends
    - Market holidays
    - Pre-market and after-hours periods

    Rate Limit: 60 requests per minute per IP

    Returns:
        dict: Market status information including:
            - is_open: Whether market is currently open
            - status: 'open' or 'closed'
            - reason: Reason for current status
            - next_open/closes_at: Timing information
            - current_time_et: Current time in ET timezone

    Example:
        GET /api/v1/stocks/market/status
    """
    return MarketStatusService.is_market_open()
