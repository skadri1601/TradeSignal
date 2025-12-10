import asyncio
import os
import sys
from datetime import datetime, timedelta
import logging

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.database import db_manager
from app.models.congressional_trade import CongressionalTrade, TradeType
from app.models.congressperson import Congressperson
from app.schemas.congressional_trade import CongressionalTradeCreate
from app.services.congressional_trade_service import CongressionalTradeService
from app.services.congressperson_service import CongresspersonService
from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def populate_congressional_data():
    """
    Populates the database with mock congressional trade and congressperson data.
    This script is intended for development and testing environments.
    """
    if not settings.debug:
        logger.warning("Data population script is intended for debug environments only. Skipping.")
        return

    logger.info("Starting population of mock congressional data...")

    await db_manager.connect()

    try:
        # Clear existing data for a clean run
        logger.info("Clearing existing CongressionalTrade and Congressperson data...")
        await db_manager.get_session().execute(CongressionalTrade.__table__.delete())
        await db_manager.get_session().execute(Congressperson.__table__.delete())
        await db_manager.get_session().commit()
        logger.info("Existing data cleared.")

        congressperson_service = CongresspersonService(db_manager.get_session())
        trade_service = CongressionalTradeService(db_manager.get_session())

        # Create mock congresspersons
        congresspersons_data = [
            {"first_name": "Nancy", "last_name": "Pelosi", "party": "Democrat", "state": "CA"},
            {"first_name": "Kevin", "last_name": "McCarthy", "party": "Republican", "state": "CA"},
            {"first_name": "Chuck", "last_name": "Schumer", "party": "Democrat", "state": "NY"},
            {"first_name": "Mitch", "last_name": "McConnell", "party": "Republican", "state": "KY"},
        ]

        congresspersons = []
        for cp_data in congresspersons_data:
            congressperson = await congressperson_service.create_congressperson(cp_data)
            congresspersons.append(congressperson)
            logger.info(f"Created congressperson: {congressperson.first_name} {congressperson.last_name}")

        # Create mock congressional trades
        trade_date_base = datetime.utcnow() - timedelta(days=30)
        trades_to_create = []

        trades_to_create.append(CongressionalTradeCreate(
            congressperson_id=congresspersons[0].id,
            company_ticker="NVDA",
            asset_type="Stock",
            trade_type=TradeType.PURCHASE,
            amount_usd="500,001 - 1,000,000",
            trade_date=trade_date_base,
            disclosure_date=trade_date_base + timedelta(days=1),
            owner_name="Spouse",
            filing_url="http://example.com/pelosi_nvda_1"
        ))
        trades_to_create.append(CongressionalTradeCreate(
            congressperson_id=congresspersons[0].id,
            company_ticker="MSFT",
            asset_type="Stock",
            trade_type=TradeType.SALE,
            amount_usd="100,001 - 250,000",
            trade_date=trade_date_base + timedelta(days=5),
            disclosure_date=trade_date_base + timedelta(days=6),
            owner_name="Self",
            filing_url="http://example.com/pelosi_msft_1"
        ))
        trades_to_create.append(CongressionalTradeCreate(
            congressperson_id=congresspersons[1].id,
            company_ticker="GOOGL",
            asset_type="Stock",
            trade_type=TradeType.PURCHASE,
            amount_usd="1,001 - 15,000",
            trade_date=trade_date_base + timedelta(days=10),
            disclosure_date=trade_date_base + timedelta(days=11),
            owner_name="Self",
            filing_url="http://example.com/mccarthy_googl_1"
        ))
        trades_to_create.append(CongressionalTradeCreate(
            congressperson_id=congresspersons[2].id,
            company_ticker="AMZN",
            asset_type="Stock",
            trade_type=TradeType.PURCHASE,
            amount_usd="15,001 - 50,000",
            trade_date=trade_date_base + timedelta(days=15),
            disclosure_date=trade_date_base + timedelta(days=16),
            owner_name="Spouse",
            filing_url="http://example.com/schumer_amzn_1"
        ))
        trades_to_create.append(CongressionalTradeCreate(
            congressperson_id=congresspersons[3].id,
            company_ticker="TSLA",
            asset_type="Stock",
            trade_type=TradeType.SALE,
            amount_usd="250,001 - 500,000",
            trade_date=trade_date_base + timedelta(days=20),
            disclosure_date=trade_date_base + timedelta(days=21),
            owner_name="Self",
            filing_url="http://example.com/mcconnell_tsla_1"
        ))

        for trade_data in trades_to_create:
            trade = await trade_service.create_congressional_trade(trade_data)
            logger.info(f"Created trade: {trade.company_ticker} ({trade.trade_type.value}) for {trade.congressperson.first_name} {trade.congressperson.last_name}")

        logger.info("Mock congressional data population complete.")

    except Exception as e:
        logger.error(f"Error populating congressional data: {e}", exc_info=True)
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    # Ensure settings are loaded
    from dotenv import load_dotenv
    load_dotenv()
    settings.load_settings() # Explicitly load settings from config.py

    logger.info(f"Running in DEBUG mode: {settings.debug}")
    asyncio.run(populate_congressional_data())
