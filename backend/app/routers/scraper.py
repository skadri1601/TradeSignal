"""
Scraper API Endpoints

Endpoints for triggering SEC Form 4 scraping operations.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.scraper_service import ScraperService

logger = logging.getLogger(__name__)

router = APIRouter()


class ScrapeRequest(BaseModel):
    """Request to scrape a company's Form 4 filings."""

    ticker: Optional[str] = Field(None, description="Company ticker symbol")
    cik: Optional[str] = Field(None, description="Company CIK")
    days_back: int = Field(30, ge=1, le=365, description="Days to look back")
    max_filings: int = Field(100, ge=1, le=100, description="Max filings to process")


class ScrapeResponse(BaseModel):
    """Response from scrape operation."""

    success: bool = Field(..., description="Whether scrape succeeded")
    filings_processed: int = Field(..., description="Number of filings processed")
    trades_created: int = Field(..., description="Number of trades created")
    errors: Optional[list] = Field(None, description="Any errors encountered")
    message: Optional[str] = Field(None, description="Additional message")


@router.post("/scrape", response_model=ScrapeResponse, status_code=200)
async def scrape_company_filings(
    request: ScrapeRequest, db: AsyncSession = Depends(get_db)
):
    """
    Scrape Form 4 filings for a company.

    Fetches recent insider trading Form 4 filings from SEC EDGAR
    and saves them to the database.

    **Parameters:**
    - `ticker`: Stock ticker symbol (e.g., "AAPL")
    - `cik`: SEC Central Index Key (alternative to ticker)
    - `days_back`: How many days back to fetch (default: 30, max: 365)
    - `max_filings`: Maximum filings to process (default: 100, max: 100)

    **Returns:**
    - Summary of scraping operation (filings processed, trades created)

    **Example:**
    ```json
    {
      "ticker": "AAPL",
      "days_back": 30,
      "max_filings": 50
    }
    ```

    **Note:** SEC rate limits to 10 requests/second. Large scrapes may take time.
    """
    if not request.ticker and not request.cik:
        raise HTTPException(status_code=400, detail="Must provide either ticker or CIK")

    logger.info(
        f"Scrape request: {request.ticker or request.cik} "
        f"(last {request.days_back} days)"
    )

    try:
        scraper = ScraperService()
        result = await scraper.scrape_company_trades(
            db=db,
            ticker=request.ticker,
            cik=request.cik,
            days_back=request.days_back,
            max_filings=request.max_filings,
        )

        return ScrapeResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/scrape/{ticker}", response_model=ScrapeResponse)
async def scrape_by_ticker(
    ticker: str,
    days_back: int = Query(30, ge=1, le=365, description="Days to look back"),
    max_filings: int = Query(100, ge=1, le=100, description="Max filings"),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick scrape by ticker (GET endpoint).

    Convenience endpoint for scraping a company by ticker.

    **Example:** `GET /api/v1/scraper/AAPL?days_back=30`
    """
    logger.info(f"Quick scrape: {ticker} (last {days_back} days)")

    try:
        scraper = ScraperService()
        result = await scraper.scrape_company_trades(
            db=db, ticker=ticker, days_back=days_back, max_filings=max_filings
        )

        return ScrapeResponse(**result)

    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/test", response_model=dict)
async def test_sec_connection():
    """
    Test connection to SEC EDGAR.

    Verifies that the SEC client is configured correctly
    and can connect to SEC EDGAR API.

    **Returns:**
    - Status of SEC connection
    """
    try:
        from app.services.sec_client import SECClient

        client = SECClient()

        return {
            "success": True,
            "message": "SEC client configured correctly",
            "user_agent": client.user_agent,
            "rate_limit": f"{client.MAX_REQUESTS_PER_SECOND} req/sec",
        }

    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "SEC_USER_AGENT not configured. Set in .env file.",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
