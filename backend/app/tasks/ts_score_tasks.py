"""
TradeSignal Score background tasks.

Real-time updates and batch processing.
"""

import asyncio
import logging
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.database import db_manager
from app.services.ts_score_service import TSScoreService

logger = logging.getLogger(__name__)


@celery_app.task(name="calculate_ts_score_for_company")
def calculate_ts_score_for_company_task(ticker: str):
    """Calculate TS Score for a single company."""
    async def _async_task():
        logger.info(f"Calculating TS Score for {ticker}...")
        try:
            async with db_manager.get_session() as db:
                service = TSScoreService(db)
                result = await service.calculate_ts_score(ticker)

                if result:
                    # Save to database
                    await service.save_ts_score(result)
                    logger.info(f"TS Score calculated for {ticker}: {result['ts_score']} ({result['badge']})")
                else:
                    logger.warning(f"Failed to calculate TS Score for {ticker}")

                return result
        except Exception as e:
            logger.error(f"Error in calculate_ts_score_for_company_task for {ticker}: {e}", exc_info=True)
            return {"error": str(e)}

    return asyncio.run(_async_task())


@celery_app.task(name="batch_update_ts_scores")
def batch_update_ts_scores_task():
    """
    Batch update TS Scores for all active companies.

    Runs periodically to keep scores up to date.
    """
    async def _async_task():
        logger.info("Starting batch TS Score update...")
        try:
            from app.models.company import Company
            from sqlalchemy import select

            async with db_manager.get_session() as db:
                # Get all active companies
                result = await db.execute(
                    select(Company).where(Company.is_active.is_(True))
                )
                companies = result.scalars().all()

                service = TSScoreService(db)
                results = {
                    "processed": 0,
                    "succeeded": 0,
                    "failed": 0,
                }

                for company in companies:
                    try:
                        results["processed"] += 1
                        score_result = await service.calculate_ts_score(company.ticker)

                        if score_result:
                            await service.save_ts_score(score_result)
                            results["succeeded"] += 1
                        else:
                            results["failed"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        logger.error(f"Error processing TS Score for {company.ticker}: {e}")

                logger.info(
                    f"Batch TS Score update complete: "
                    f"{results['succeeded']}/{results['processed']} succeeded"
                )

                return results
        except Exception as e:
            logger.error(f"Error in batch_update_ts_scores_task: {e}", exc_info=True)
            return {"error": str(e)}

    return asyncio.run(_async_task())


