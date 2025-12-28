"""
Market Data API Routes

Endpoints for dividends, earnings, recommendations, financials, etc.
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.yfinance_service import YFinanceService
from app.services.finnhub_service import FinnhubService

router = APIRouter(prefix="/market-data", tags=["Market Data"])

# Service instances
yfinance_service = YFinanceService()
finnhub_service = FinnhubService()


# ============ yfinance endpoints (no rate limit) ============

@router.get("/dividends/{ticker}")
async def get_dividends(
    ticker: str,
    refresh: bool = Query(False, description="Force refresh from API"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dividend history for a stock.

    Source: yfinance (no rate limit)
    Cache: 24 hours
    """
    dividends = await yfinance_service.get_dividends(db, ticker, force_refresh=refresh)
    return {"ticker": ticker.upper(), "dividends": dividends}


@router.get("/earnings-calendar/{ticker}")
async def get_earnings_calendar(
    ticker: str,
    refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Get next earnings date and estimates.

    Source: yfinance (no rate limit)
    Cache: 6 hours
    """
    data = await yfinance_service.get_earnings_calendar(db, ticker, force_refresh=refresh)
    return {"ticker": ticker.upper(), **data}


@router.get("/recommendations/{ticker}")
async def get_recommendations(
    ticker: str,
    refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Get analyst recommendations (buy/hold/sell).

    Source: yfinance (no rate limit)
    Cache: 6 hours
    """
    recs = await yfinance_service.get_analyst_recommendations(db, ticker, force_refresh=refresh)

    # Calculate summary
    if recs:
        latest = recs[0]
        total = latest['strong_buy'] + latest['buy'] + latest['hold'] + latest['sell'] + latest['strong_sell']
        summary = {
            "total_analysts": total,
            "buy_percent": round((latest['strong_buy'] + latest['buy']) / total * 100, 1) if total else 0,
            "hold_percent": round(latest['hold'] / total * 100, 1) if total else 0,
            "sell_percent": round((latest['sell'] + latest['strong_sell']) / total * 100, 1) if total else 0,
        }
    else:
        summary = {}

    return {"ticker": ticker.upper(), "summary": summary, "history": recs}


@router.get("/financials/{ticker}")
async def get_financials(
    ticker: str,
    statement: str = Query("income", enum=["income", "balance", "cashflow"]),
    period: str = Query("quarterly", enum=["quarterly", "annual"]),
    refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Get financial statements.

    Source: yfinance (no rate limit)
    Cache: 24 hours
    """
    data = await yfinance_service.get_financial_statements(
        db, ticker,
        statement_type=statement,
        period=period,
        force_refresh=refresh
    )
    return {
        "ticker": ticker.upper(),
        "statement_type": statement,
        "period": period,
        "statements": data,
    }


# ============ Finnhub endpoints (60 calls/min limit) ============

@router.get("/price-target/{ticker}")
async def get_price_target(
    ticker: str,
    refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Get analyst price targets.

    Source: Finnhub (rate limited)
    Cache: 6 hours
    """
    data = await finnhub_service.get_price_target(db, ticker, force_refresh=refresh)
    if not data:
        raise HTTPException(404, f"No price target data for {ticker}")
    return {"ticker": ticker.upper(), **data}


@router.get("/earnings-surprises/{ticker}")
async def get_earnings_surprises(
    ticker: str,
    limit: int = Query(4, ge=1, le=20),
    refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    Get earnings surprises (actual vs estimate).

    Source: Finnhub (rate limited)
    Cache: 6 hours
    """
    data = await finnhub_service.get_earnings_surprises(db, ticker, limit, force_refresh=refresh)
    return {"ticker": ticker.upper(), "earnings": data}


@router.get("/ipo-calendar")
async def get_ipo_calendar(
    from_date: Optional[date] = Query(None, description="Start date (default: today)"),
    to_date: Optional[date] = Query(None, description="End date (default: +30 days)"),
    refresh: bool = Query(False),
):
    """
    Get upcoming IPOs.

    Source: Finnhub (rate limited)
    Cache: 1 hour
    """
    data = await finnhub_service.get_ipo_calendar(from_date, to_date, force_refresh=refresh)
    return {"ipos": data}


@router.get("/economic-calendar")
async def get_economic_calendar(
    from_date: Optional[date] = Query(None, description="Start date (default: today)"),
    to_date: Optional[date] = Query(None, description="End date (default: +14 days)"),
    refresh: bool = Query(False),
):
    """
    Get economic events (Fed meetings, CPI, jobs, etc.).

    Source: Finnhub (rate limited)
    Cache: 1 hour
    """
    data = await finnhub_service.get_economic_calendar(from_date, to_date, force_refresh=refresh)
    return {"events": data}


# ============ Combined endpoint for stock detail page ============

@router.get("/stock-overview/{ticker}")
async def get_stock_overview(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all market data for a stock in one call.

    Combines: earnings calendar, recommendations, price target.
    Useful for stock detail pages.
    """
    # These run in parallel (sort of - Python async)
    earnings = await yfinance_service.get_earnings_calendar(db, ticker)
    recommendations = await yfinance_service.get_analyst_recommendations(db, ticker)
    price_target = await finnhub_service.get_price_target(db, ticker)

    # Summary
    rec_summary = {}
    if recommendations:
        latest = recommendations[0]
        total = latest['strong_buy'] + latest['buy'] + latest['hold'] + latest['sell'] + latest['strong_sell']
        if total > 0:
            buy_count = latest['strong_buy'] + latest['buy']
            sell_count = latest['sell'] + latest['strong_sell']
            rec_summary = {
                "consensus": "BUY" if buy_count > total / 2 else (
                    "SELL" if sell_count > total / 2 else "HOLD"
                ),
                "total_analysts": total,
            }

    return {
        "ticker": ticker.upper(),
        "earnings": earnings,
        "recommendations": rec_summary,
        "price_target": price_target,
    }

