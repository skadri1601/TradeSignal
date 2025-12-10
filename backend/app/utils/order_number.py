"""
Order number generation utility.

Generates unique order numbers for subscriptions in the format:
ORD-{YYYYMMDD}-{USER_ID}-{RANDOM_6_CHARS}
"""

import random
import string
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.subscription import Subscription


def generate_random_chars(length: int = 6) -> str:
    """Generate random alphanumeric uppercase characters."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def generate_order_number(user_id: int, db: AsyncSession) -> str:
    """
    Generate a unique order number for a subscription.
    
    Format: ORD-{YYYYMMDD}-{USER_ID}-{RANDOM_6_CHARS}
    
    Args:
        user_id: The user ID for the subscription
        db: Database session
        
    Returns:
        Unique order number string
        
    Raises:
        Exception: If unable to generate unique order number after 5 attempts
    """
    date_str = datetime.utcnow().strftime('%Y%m%d')
    max_attempts = 5
    
    for attempt in range(max_attempts):
        random_chars = generate_random_chars(6)
        order_number = f"ORD-{date_str}-{user_id}-{random_chars}"
        
        # Check if order number already exists
        result = await db.execute(
            select(Subscription).where(Subscription.order_number == order_number)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            return order_number
    
    # If we couldn't generate a unique number after max attempts, raise an error
    raise Exception(
        f"Unable to generate unique order number after {max_attempts} attempts"
    )

