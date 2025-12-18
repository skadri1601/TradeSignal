"""
Initialize research data tables in the database.

Creates tables for IntrinsicValueTarget, TradeSignalScore, and RiskLevelAssessment
if they don't already exist.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_manager, Base
from app.models import (
    IntrinsicValueTarget,
    TradeSignalScore,
    RiskLevelAssessment
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_research_tables():
    """Create research data tables if they don't exist."""
    logger.info("=" * 80)
    logger.info("Initializing Research Data Tables")
    logger.info("=" * 80)
    
    try:
        engine = db_manager.get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Research tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize research tables: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(init_research_tables())
