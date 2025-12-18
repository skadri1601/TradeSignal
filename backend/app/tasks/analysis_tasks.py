from app.core.celery_app import celery_app
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from app.database import db_manager
from app.services.pattern_analysis_service import PatternAnalysisService
from app.models.company import Company
from app.core.redis_cache import get_cache
import json
import asyncio

logger = logging.getLogger(__name__)
redis = get_cache()

@celery_app.task(name="analyze_company_patterns")
def analyze_company_patterns_task(ticker: str, days_back: int = 90):
    """
    Celery task to analyze patterns for a specific company and cache the result.
    """
    async def _async_task():
        logger.info(f"Starting pattern analysis for {ticker}...")
        try:
            async with db_manager.get_session() as db:
                service = PatternAnalysisService(db)
                result = await service.analyze_company_patterns(ticker, days_back)
                
                # Cache the result
                if redis.enabled():
                    cache_key = f"patterns:{ticker}:{days_back}"
                    # Redis expects string, byte, int or float. Dict needs serialization.
                    # PatternAnalysisService returns a dict.
                    # Use standard json serialization (PatternAnalysisService handles date serialization if needed?
                    # Actually, analyze_company_patterns might return objects that need serialization.
                    # Let's rely on service returning serializable dict, or handle it here.
                    # Looking at service code, it returns simple types mostly, but maybe nested dicts.
                    
                    # We need to handle potential serialization issues (e.g. datetime objects if any remain)
                    # But analyze_company_patterns returns a dict designed for API response, so it should be mostly serializable.
                    redis.set(cache_key, result, ttl=3600 * 24) # Cache for 24 hours
                    logger.info(f"Cached pattern analysis for {ticker}")
                
                return result
        except Exception as e:
            logger.error(f"Error in analyze_company_patterns_task for {ticker}: {e}", exc_info=True)
            return {"error": str(e)}
    
    return asyncio.run(_async_task())

@celery_app.task(name="analyze_all_active_companies_patterns")
def analyze_all_active_companies_patterns_task():
    """
    Orchestrator task to analyze patterns for all active companies.
    """
    async def _async_task():
        logger.info("Starting analysis of all active companies...")
        async with db_manager.get_session() as db:
            # Fetch active companies (maybe limit to those with recent trades to save resources)
            # For now, get all active companies
            companies_result = await db.execute(select(Company).filter(Company.is_active == True))
            companies = companies_result.scalars().all()
            
            for company in companies:
                analyze_company_patterns_task.delay(company.ticker)
                
        logger.info(f"Enqueued pattern analysis for {len(companies)} companies.")
    
    asyncio.run(_async_task())

@celery_app.task(name="precompute_top_patterns")
def precompute_top_patterns_task():
    """
    Task to pre-compute 'get_top_patterns' for all supported pattern types.
    """
    async def _async_task():
        logger.info("Starting pre-computation of top patterns...")
        pattern_types = ["BUYING_MOMENTUM", "SELLING_PRESSURE", "CLUSTER", "REVERSAL"]
        
        try:
            async with db_manager.get_session() as db:
                service = PatternAnalysisService(db)
                
                for p_type in pattern_types:
                    logger.info(f"Analyzing top patterns for {p_type}...")
                    results = await service.get_top_patterns(pattern_type=p_type, limit=10)
                    
                    if redis.enabled():
                        cache_key = f"patterns:top:{p_type}"
                        redis.set(cache_key, results, ttl=3600 * 6) # Cache for 6 hours
                        logger.info(f"Cached top patterns for {p_type}")
                        
        except Exception as e:
            logger.error(f"Error in precompute_top_patterns_task: {e}", exc_info=True)
    
    asyncio.run(_async_task())
