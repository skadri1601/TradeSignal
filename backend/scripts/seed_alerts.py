"""
Seed test alerts into the database.

This script creates sample alert configurations for testing the alert system.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_manager
from app.models import Alert
from sqlalchemy import select


async def create_sample_alerts():
    """Create sample alert configurations."""

    async with db_manager.get_session() as session:
        # Check if alerts already exist
        result = await session.execute(select(Alert))
        existing = result.scalars().all()

        if existing:
            print(f"⚠️  Found {len(existing)} existing alerts. Skipping seed.")
            print("Delete existing alerts first if you want to re-seed.")
            return

        print("Creating sample alerts...")

        # Sample alerts
        sample_alerts = [
            Alert(
                name="Large NVIDIA Trades",
                alert_type="large_trade",
                ticker="NVDA",
                min_value=1000000,  # $1M+
                transaction_type=None,  # Any type
                notification_channels=["webhook"],
                webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                is_active=True
            ),
            Alert(
                name="Apple Insider Buys",
                alert_type="company_watch",
                ticker="AAPL",
                min_value=500000,  # $500K+
                transaction_type="BUY",
                notification_channels=["webhook"],
                webhook_url="https://discord.com/api/webhooks/YOUR/WEBHOOK",
                is_active=True
            ),
            Alert(
                name="Tesla CEO/CFO Activity",
                alert_type="insider_role",
                ticker="TSLA",
                min_value=100000,  # $100K+
                transaction_type=None,
                insider_roles=["CEO", "CFO"],
                notification_channels=["webhook"],
                webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                is_active=True
            ),
            Alert(
                name="Large Tech Sells ($10M+)",
                alert_type="large_trade",
                ticker=None,  # Any company
                min_value=10000000,  # $10M+
                transaction_type="SELL",
                notification_channels=["webhook"],
                webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                is_active=True
            ),
            Alert(
                name="Microsoft Watch (Inactive)",
                alert_type="company_watch",
                ticker="MSFT",
                min_value=250000,  # $250K+
                transaction_type=None,
                notification_channels=["webhook"],
                webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                is_active=False  # Inactive for testing
            ),
            Alert(
                name="Palantir Large Buys",
                alert_type="large_trade",
                ticker="PLTR",
                min_value=2000000,  # $2M+
                transaction_type="BUY",
                notification_channels=["webhook"],
                webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                is_active=True
            ),
        ]

        # Add to session
        for alert in sample_alerts:
            session.add(alert)

        await session.commit()

        print(f"✅ Created {len(sample_alerts)} sample alerts!")
        print("\nCreated alerts:")
        for i, alert in enumerate(sample_alerts, 1):
            status = "✓ Active" if alert.is_active else "✗ Inactive"
            print(f"  {i}. {alert.name} ({alert.alert_type}) - {status}")

        print("\n💡 Note: Webhook URLs are placeholders. Update them in the UI to test notifications.")


async def main():
    """Main entry point."""
    print("=" * 60)
    print("TradeSignal - Alert Seeder")
    print("=" * 60)
    print()

    try:
        await create_sample_alerts()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("=" * 60)
    print("Seeding complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
