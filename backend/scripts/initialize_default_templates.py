"""
Script to initialize default email templates.

Run this script to create default email templates for marketing campaigns.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_manager
from app.services.email_template_service import EmailTemplateService


async def main():
    """Initialize default email templates."""
    print("Initializing default email templates...")
    
    async with db_manager.get_session() as db:
        template_service = EmailTemplateService(db)
        
        try:
            templates = await template_service.create_default_templates()
            print(f"✅ Created {len(templates)} default templates:")
            for name, template in templates.items():
                print(f"  - {name}: {template.name} (ID: {template.id})")
        except Exception as e:
            print(f"❌ Error creating templates: {e}")
            # Check if templates already exist
            if "already exists" in str(e) or "unique constraint" in str(e).lower():
                print("⚠️  Templates may already exist. Skipping...")
            else:
                raise


if __name__ == "__main__":
    asyncio.run(main())

