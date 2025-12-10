import asyncio
import sys
import os
import logging
from sqlalchemy import select

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.database import db_manager
from app.models.user import User

async def check_users():
    logger.info("Connecting to database...")
    try:
        async with db_manager.get_session() as session:
            logger.info("Connected. Fetching users...")
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                logger.info("No users found in database.")
                return

            logger.info(f"Found {len(users)} users:")
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Active: {user.is_active}, Verified: {user.is_verified}")
                
    except Exception as e:
        logger.error(f"Error checking users: {repr(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_users())
