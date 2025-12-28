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

    success: bool = Field(..., description="Whether scrape initiation succeeded")
    message: str = Field(..., description="Additional message")
    task_id: Optional[str] = Field(None, description="Task ID (deprecated - Celery removed)")


@router.post("/scrape", response_model=ScrapeResponse, status_code=202) # Use 202 Accepted for async operation
async def scrape_company_filings(
    request: ScrapeRequest, db: AsyncSession = Depends(get_db)
):
    """
    Initiate asynchronous scraping of Form 4 filings for a company.

    **Parameters:**
    - `ticker`: Stock ticker symbol (e.g., "AAPL")
    - `cik`: SEC Central Index Key (alternative to ticker)

    **Returns:**
    - A message indicating that the scraping task has been initiated and its task ID.
    """
    if not request.ticker and not request.cik:
        raise HTTPException(status_code=400, detail="Must provide either ticker or CIK")

    logger.info(
        f"Scrape initiation request received for: {request.ticker or request.cik}"
    )

    try:
        scraper = ScraperService()
        result = await scraper.scrape_company_trades(
            db=db, # Pass db for company lookup
            ticker=request.ticker,
            cik=request.cik,
            # days_back and max_filings are now handled by background task config
        )

        return ScrapeResponse(
            success=True,
            message=result.get("message", "Scraping task initiated."),
            task_id=result.get("task_id"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Scrape initiation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping initiation failed: {str(e)}")


@router.get("/scrape/{ticker}", response_model=ScrapeResponse, status_code=202) # Use 202 Accepted for async operation
async def scrape_by_ticker(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate asynchronous scraping of Form 4 filings for a company by ticker.

    **Parameters:**
    - `ticker`: Stock ticker symbol

    **Returns:**
    - A message indicating that the scraping task has been initiated and its task ID.

    **Example:** `GET /api/v1/scraper/AAPL`
    """
    logger.info(f"Quick scrape initiation request for: {ticker}")

    try:
        scraper = ScraperService()
        result = await scraper.scrape_company_trades(
            db=db, # Pass db for company lookup
            ticker=ticker,
            # days_back and max_filings are now handled by background task config
        )

        return ScrapeResponse(
            success=True,
            message=result.get("message", f"Scraping task initiated for {ticker}."),
            task_id=result.get("task_id"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Scrape initiation failed for {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping initiation failed: {str(e)}")


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
