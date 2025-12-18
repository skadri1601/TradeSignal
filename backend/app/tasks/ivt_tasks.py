"""
IVT (Intrinsic Value Target) background tasks.

Nightly batch processing for IVT calculations.
"""

import asyncio
import logging
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.database import db_manager
from app.services.ivt_data_service import IVTDataService

logger = logging.getLogger(__name__)


@celery_app.task(name="calculate_ivt_for_company")
def calculate_ivt_for_company_task(ticker: str):
    """Calculate IVT for a single company."""
    async def _async_task():
        logger.info(f"Starting IVT calculation for {ticker}...")
        try:
            async with db_manager.get_session() as db:
                service = IVTDataService(db)
                result = await service.calculate_ivt_for_company(ticker)

                if result:
                    logger.info(f"IVT calculated for {ticker}: ${result.get('intrinsic_value', 0):.2f}")
                else:
                    logger.warning(f"Failed to calculate IVT for {ticker}")

                return result
        except Exception as e:
            logger.error(f"Error in calculate_ivt_for_company_task for {ticker}: {e}", exc_info=True)
            return {"error": str(e)}

    return asyncio.run(_async_task())


@celery_app.task(name="batch_process_ivt_calculations")
def batch_process_ivt_calculations_task(tickers: list = None):
    """
    Batch process IVT calculations for all companies.

    Runs nightly to update IVT values.
    """
    async def _async_task():
        logger.info("Starting batch IVT processing...")
        try:
            async with db_manager.get_session() as db:
                service = IVTDataService(db)
                results = await service.batch_process_ivt_calculations(tickers)

                logger.info(
                    f"Batch IVT processing complete: "
                    f"{results['succeeded']}/{results['processed']} succeeded, "
                    f"{results['failed']} failed"
                )

                return results
        except Exception as e:
            logger.error(f"Error in batch_process_ivt_calculations_task: {e}", exc_info=True)
            return {"error": str(e)}

    return asyncio.run(_async_task())


