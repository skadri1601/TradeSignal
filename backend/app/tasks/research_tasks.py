"""
Celery tasks for research feature batch processing.

Handles:
- Pre-calculation of competitive strength scores
- Pre-calculation of management scores
- Batch processing for popular tickers
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.celery_app import celery_app
from app.database import db_manager
from app.services.competitive_strength_service import CompetitiveStrengthService
from app.services.management_score_service import ManagementScoreService
from app.services.cache_service import cache_service
from app.models.company import Company
from app.models.trade import Trade
from app.models.competitive_strength import CompetitiveStrengthRating
from app.models.management_score import ManagementScore
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

logger = logging.getLogger(__name__)


@celery_app.task(name="precalculate_competitive_strength_batch")
def precalculate_competitive_strength_batch_task(tickers: List[str]):
    """
    Pre-calculate competitive strength scores for a batch of tickers.
    
    Args:
        tickers: List of ticker symbols to process
    """
    async def _async_task():
        logger.info(f"Starting competitive strength batch calculation for {len(tickers)} tickers")
        
        async with db_manager.get_session() as db:
            strength_service = CompetitiveStrengthService(db)
            results = {
                "processed": 0,
                "succeeded": 0,
                "failed": 0,
                "errors": []
            }
            
            for ticker in tickers:
                try:
                    results["processed"] += 1
                    ticker = ticker.upper()
                    
                    # Check if already calculated recently (within last 7 days)
                    result = await db.execute(
                        select(CompetitiveStrengthRating)
                        .where(CompetitiveStrengthRating.ticker == ticker)
                        .order_by(CompetitiveStrengthRating.calculated_at.desc())
                        .limit(1)
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        days_old = (datetime.utcnow() - existing.calculated_at.replace(tzinfo=None)).days
                        if days_old < 7:
                            logger.debug(f"Skipping {ticker}: calculated {days_old} days ago")
                            continue
                    
                    # Calculate with real financial data (will fetch automatically)
                    calculation_result = await strength_service.calculate_competitive_strength(ticker=ticker)
                    
                    # Save to database
                    comp_rating = CompetitiveStrengthRating(
                        ticker=ticker,
                        rating=calculation_result["rating"],
                        composite_score=calculation_result["composite_score"],
                        network_effects_score=calculation_result["component_scores"]["network_effects"],
                        intangible_assets_score=calculation_result["component_scores"]["intangible_assets"],
                        cost_advantages_score=calculation_result["component_scores"]["cost_advantages"],
                        switching_costs_score=calculation_result["component_scores"]["switching_costs"],
                        efficient_scale_score=calculation_result["component_scores"]["efficient_scale"],
                        trajectory=calculation_result["trajectory"],
                        calculated_at=datetime.utcnow(),
                    )
                    db.add(comp_rating)
                    await db.commit()
                    
                    # Invalidate cache
                    await cache_service.delete(f"competitive_strength:{ticker}:latest")
                    
                    results["succeeded"] += 1
                    logger.debug(f"Successfully calculated competitive strength for {ticker}")
                    
                    # Rate limiting delay
                    if settings.batch_processing_rate_limit_delay > 0:
                        await asyncio.sleep(settings.batch_processing_rate_limit_delay)
                        
                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"{ticker}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(f"Error calculating competitive strength for {ticker}: {e}", exc_info=True)
            
            logger.info(
                f"Competitive strength batch calculation complete: "
                f"{results['succeeded']} succeeded, {results['failed']} failed out of {results['processed']} processed"
            )
            return results
    
    return asyncio.run(_async_task())


@celery_app.task(name="precalculate_management_score_batch")
def precalculate_management_score_batch_task(tickers: List[str]):
    """
    Pre-calculate management scores for a batch of tickers.
    
    Args:
        tickers: List of ticker symbols to process
    """
    async def _async_task():
        logger.info(f"Starting management score batch calculation for {len(tickers)} tickers")
        
        async with db_manager.get_session() as db:
            management_service = ManagementScoreService(db)
            results = {
                "processed": 0,
                "succeeded": 0,
                "failed": 0,
                "errors": []
            }
            
            for ticker in tickers:
                try:
                    results["processed"] += 1
                    ticker = ticker.upper()
                    
                    # Check if already calculated recently (within last 7 days)
                    result = await db.execute(
                        select(ManagementScore)
                        .where(ManagementScore.ticker == ticker)
                        .order_by(ManagementScore.calculated_at.desc())
                        .limit(1)
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        days_old = (datetime.utcnow() - existing.calculated_at.replace(tzinfo=None)).days
                        if days_old < 7:
                            logger.debug(f"Skipping {ticker}: calculated {days_old} days ago")
                            continue
                    
                    # Calculate with default values (will be enhanced with real data)
                    calculation_result = await management_service.calculate_management_score(ticker=ticker)
                    
                    # Save to database
                    mgmt_score = ManagementScore(
                        ticker=ticker,
                        grade=calculation_result["grade"],
                        composite_score=calculation_result["composite_score"],
                        m_and_a_score=calculation_result["component_scores"]["m_and_a"],
                        capital_discipline_score=calculation_result["component_scores"]["capital_discipline"],
                        shareholder_returns_score=calculation_result["component_scores"]["shareholder_returns"],
                        leverage_management_score=calculation_result["component_scores"]["leverage_management"],
                        governance_score=calculation_result["component_scores"]["governance"],
                        calculated_at=datetime.utcnow(),
                    )
                    db.add(mgmt_score)
                    await db.commit()
                    
                    # Invalidate cache
                    await cache_service.delete(f"management_score:{ticker}:latest")
                    
                    results["succeeded"] += 1
                    logger.debug(f"Successfully calculated management score for {ticker}")
                    
                    # Rate limiting delay
                    if settings.batch_processing_rate_limit_delay > 0:
                        await asyncio.sleep(settings.batch_processing_rate_limit_delay)
                        
                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"{ticker}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(f"Error calculating management score for {ticker}: {e}", exc_info=True)
            
            logger.info(
                f"Management score batch calculation complete: "
                f"{results['succeeded']} succeeded, {results['failed']} failed out of {results['processed']} processed"
            )
            return results
    
    return asyncio.run(_async_task())


@celery_app.task(name="precalculate_popular_tickers_scores")
def precalculate_popular_tickers_scores_task():
    """
    Pre-calculate scores for popular tickers.
    
    Identifies popular tickers based on:
    - Companies with most insider trades (default)
    - Market cap (if configured)
    - User watchlists (if tracking exists)
    """
    async def _async_task():
        logger.info("Starting pre-calculation for popular tickers")
        
        async with db_manager.get_session() as db:
            # Get popular tickers based on configuration
            if settings.popular_tickers_source == "trade_volume":
                # Get tickers with most insider trades in last 90 days
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                result = await db.execute(
                    select(Company.ticker, func.count(Trade.id).label("trade_count"))
                    .join(Trade, Company.id == Trade.company_id)
                    .where(Trade.transaction_date >= cutoff_date)
                    .group_by(Company.ticker)
                    .order_by(desc("trade_count"))
                    .limit(settings.popular_tickers_count)
                )
                popular_tickers = [row[0] for row in result.all() if row[0]]
            else:
                # Default: Get all active companies (limited by popular_tickers_count)
                result = await db.execute(
                    select(Company.ticker)
                    .where(Company.is_active.is_(True))
                    .limit(settings.popular_tickers_count)
                )
                popular_tickers = [row[0] for row in result.all() if row[0]]
            
            if not popular_tickers:
                logger.warning("No popular tickers found to process")
                return {"processed": 0, "succeeded": 0, "failed": 0}
            
            logger.info(f"Found {len(popular_tickers)} popular tickers to process")
            
            # Process in batches
            batch_size = settings.batch_processing_batch_size
            total_succeeded = 0
            total_failed = 0
            
            for i in range(0, len(popular_tickers), batch_size):
                batch = popular_tickers[i:i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} tickers)")
                
                # Calculate competitive strength
                comp_result = precalculate_competitive_strength_batch_task.delay(batch)
                comp_results = comp_result.get(timeout=300)  # 5 minute timeout
                total_succeeded += comp_results.get("succeeded", 0)
                total_failed += comp_results.get("failed", 0)
                
                # Calculate management scores
                mgmt_result = precalculate_management_score_batch_task.delay(batch)
                mgmt_results = mgmt_result.get(timeout=300)  # 5 minute timeout
                total_succeeded += mgmt_results.get("succeeded", 0)
                total_failed += mgmt_results.get("failed", 0)
            
            logger.info(
                f"Popular tickers pre-calculation complete: "
                f"{total_succeeded} succeeded, {total_failed} failed"
            )
            return {
                "processed": len(popular_tickers),
                "succeeded": total_succeeded,
                "failed": total_failed
            }
    
    return asyncio.run(_async_task())


@celery_app.task(name="batch_calculate_competitive_strength")
def batch_calculate_competitive_strength_task():
    """
    Batch calculate competitive strength for all active companies.
    Runs weekly to update all scores.
    """
    async def _async_task():
        logger.info("Starting batch competitive strength calculation for all active companies")
        
        async with db_manager.get_session() as db:
            # Get all active companies
            result = await db.execute(
                select(Company.ticker)
                .where(Company.is_active.is_(True))
                .limit(settings.batch_processing_max_tickers_per_run)
            )
            all_tickers = [row[0] for row in result.all() if row[0]]
            
            if not all_tickers:
                logger.warning("No active companies found to process")
                return {"processed": 0, "succeeded": 0, "failed": 0}
            
            logger.info(f"Processing {len(all_tickers)} active companies")
            
            # Process in batches
            batch_size = settings.batch_processing_batch_size
            total_succeeded = 0
            total_failed = 0
            
            for i in range(0, len(all_tickers), batch_size):
                batch = all_tickers[i:i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1} of {(len(all_tickers) + batch_size - 1) // batch_size} ({len(batch)} tickers)")
                
                result = precalculate_competitive_strength_batch_task.delay(batch)
                batch_results = result.get(timeout=600)  # 10 minute timeout per batch
                total_succeeded += batch_results.get("succeeded", 0)
                total_failed += batch_results.get("failed", 0)
            
            logger.info(
                f"Batch competitive strength calculation complete: "
                f"{total_succeeded} succeeded, {total_failed} failed out of {len(all_tickers)} processed"
            )
            return {
                "processed": len(all_tickers),
                "succeeded": total_succeeded,
                "failed": total_failed
            }
    
    return asyncio.run(_async_task())


@celery_app.task(name="batch_calculate_management_scores")
def batch_calculate_management_scores_task():
    """
    Batch calculate management scores for all active companies.
    Runs weekly to update all scores.
    """
    async def _async_task():
        logger.info("Starting batch management score calculation for all active companies")
        
        async with db_manager.get_session() as db:
            # Get all active companies
            result = await db.execute(
                select(Company.ticker)
                .where(Company.is_active.is_(True))
                .limit(settings.batch_processing_max_tickers_per_run)
            )
            all_tickers = [row[0] for row in result.all() if row[0]]
            
            if not all_tickers:
                logger.warning("No active companies found to process")
                return {"processed": 0, "succeeded": 0, "failed": 0}
            
            logger.info(f"Processing {len(all_tickers)} active companies")
            
            # Process in batches
            batch_size = settings.batch_processing_batch_size
            total_succeeded = 0
            total_failed = 0
            
            for i in range(0, len(all_tickers), batch_size):
                batch = all_tickers[i:i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1} of {(len(all_tickers) + batch_size - 1) // batch_size} ({len(batch)} tickers)")
                
                result = precalculate_management_score_batch_task.delay(batch)
                batch_results = result.get(timeout=600)  # 10 minute timeout per batch
                total_succeeded += batch_results.get("succeeded", 0)
                total_failed += batch_results.get("failed", 0)
            
            logger.info(
                f"Batch management score calculation complete: "
                f"{total_succeeded} succeeded, {total_failed} failed out of {len(all_tickers)} processed"
            )
            return {
                "processed": len(all_tickers),
                "succeeded": total_succeeded,
                "failed": total_failed
            }
    
    return asyncio.run(_async_task())

