"""
AI-powered insights background tasks.

Generates daily summaries and caches AI insights.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.core.celery_app import celery_app
from app.database import db_manager
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_daily_ai_summary")
def generate_daily_ai_summary_task():
    """
    Generate daily AI summary at 6 AM EST (11 AM UTC).

    Filters material trades ($50K+ or 10K+ shares) and generates
    contextual analysis with historical context and sector implications.
    """
    async def _async_task():
        logger.info("Starting daily AI summary generation...")
        try:
            async with db_manager.get_session() as db:
                service = AIService(db)
                
                # Generate summary with material trade filtering
                result = await service.generate_daily_summary_material_only()
                
                if result and "error" not in result:
                    logger.info(
                        f"Daily AI summary generated successfully. "
                        f"Companies: {len(result.get('company_summaries', []))}, "
                        f"Total trades: {result.get('total_trades', 0)}"
                    )
                else:
                    error_msg = result.get("error", "Unknown error") if result else "No result"
                    logger.error(f"Failed to generate daily AI summary: {error_msg}")
                
                return result
        except Exception as e:
            logger.error(f"Error in generate_daily_ai_summary_task: {e}", exc_info=True)
            return {"error": str(e)}
    
    return asyncio.run(_async_task())


@celery_app.task(name="cache_ai_insights")
def cache_ai_insights_task(ticker: str, days_back: int = 30):
    """
    Pre-cache AI insights for a specific company.

    Useful for warming up cache before users request analysis.
    """
    async def _async_task():
        logger.info(f"Caching AI insights for {ticker}...")
        try:
            async with db_manager.get_session() as db:
                service = AIService(db)
                result = await service.analyze_company(ticker, days_back)
                
                if result and "error" not in result:
                    logger.info(f"AI insights cached for {ticker}")
                else:
                    logger.warning(f"Failed to cache AI insights for {ticker}")
                
                return result
        except Exception as e:
            logger.error(f"Error in cache_ai_insights_task for {ticker}: {e}", exc_info=True)
            return {"error": str(e)}
    
    return asyncio.run(_async_task())

