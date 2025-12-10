import asyncio
import sys
import os
from sqlalchemy import select

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import db_manager
from app.models.user import User
from app.core.security import verify_password, get_password_hash

async def check_users():
    print("Connecting to database...")
    try:
        async with db_manager.get_session() as session:
            print("Connected. Fetching users...")
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("No users found in database.")
                return

            print(f"Found {len(users)} users:")
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Active: {user.is_active}, Verified: {user.is_verified}")
                
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())
