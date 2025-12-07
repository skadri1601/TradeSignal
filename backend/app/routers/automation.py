"""
Automation API Endpoints

Provides manual triggers for automation workflows.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any

from app.services.automation_service import automation_service
from app.core.security import get_current_superuser

logger = logging.getLogger(__name__)

router = APIRouter()


class AutomationResponse(BaseModel):
    """Response from automation trigger."""

    success: bool
    message: str
    job_id: str | None = None


@router.post("/trigger-full-automation", response_model=Dict[str, Any])
async def trigger_full_automation(
    background_tasks: BackgroundTasks, current_user=Depends(get_current_superuser)
):
    """
    Manually trigger complete automation workflow.

    Requires superuser permissions.

    This will:
    1. Scrape all 183 companies from watchlist
    2. Generate AI insights for significant trades
    3. Create daily market summary
    4. Update news feed
    5. Generate trade signals

    **Note:** This runs in the background and may take 30-60 minutes.
    """
    try:
        logger.info(f"Manual automation trigger by user {current_user.email}")

        # Run automation in background
        background_tasks.add_task(automation_service.run_full_automation_cycle)

        return {
            "success": True,
            "message": "Full automation cycle started in background",
            "info": {
                "total_companies": 183,
                "estimated_duration_minutes": "30-60",
                "steps": [
                    "Scraping all companies for insider trades",
                    "Generating AI insights",
                    "Creating daily summary",
                    "Updating news feed",
                    "Generating trade signals",
                ],
            },
        }

    except Exception as e:
        logger.error(f"Failed to trigger automation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Automation trigger failed: {str(e)}"
        )


@router.post("/trigger-scrape-all", response_model=Dict[str, Any])
async def trigger_scrape_all(
    background_tasks: BackgroundTasks, current_user=Depends(get_current_superuser)
):
    """
    Manually trigger scraping of all companies only (no AI/insights).

    Requires superuser permissions.

    This will scrape all 183 companies from the watchlist for insider trades.

    **Note:** This runs in background and may take 20-30 minutes.
    """
    try:
        logger.info(f"Manual scrape-all trigger by user {current_user.email}")

        # Run scraping in background
        background_tasks.add_task(automation_service._scrape_all_companies)

        return {
            "success": True,
            "message": "Scraping all companies started in background",
            "info": {
                "total_companies": 183,
                "estimated_duration_minutes": "20-30",
                "days_back": 30,
                "max_filings_per_company": 50,
            },
        }

    except Exception as e:
        logger.error(f"Failed to trigger scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scrape trigger failed: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_automation_status(current_user=Depends(get_current_superuser)):
    """
    Get current automation system status.

    Requires superuser permissions.

    Returns information about:
    - Scheduler status
    - Last automation run
    - Next scheduled run
    - Configuration
    """
    try:
        from app.services.scheduler_service import scheduler_service
        from app.config import settings

        is_running = scheduler_service.is_running()
        jobs = scheduler_service.get_jobs()

        return {
            "scheduler_running": is_running,
            "scheduled_jobs": len(jobs),
            "timezone": settings.scraper_timezone,
            "schedule_hours": settings.scraper_schedule_hours,
            "scraper_config": {
                "days_back": settings.scraper_days_back,
                "max_filings": settings.scraper_max_filings,
                "cooldown_hours": settings.scraper_cooldown_hours,
            },
            "total_companies_in_watchlist": 183,
            "automation_enabled": True,
        }

    except Exception as e:
        logger.error(f"Failed to get automation status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
