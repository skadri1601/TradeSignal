"""
Script to validate environment configuration.

Checks all required environment variables and configuration.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings


def check_required_vars() -> List[Dict[str, Any]]:
    """Check required environment variables."""
    required_vars = [
        ("DATABASE_URL", "PostgreSQL database connection string"),
        ("SECRET_KEY", "JWT secret key for token signing"),
        ("FRONTEND_URL", "Frontend application URL"),
    ]
    
    optional_vars = [
        ("REDIS_URL", "Redis connection URL (optional, for caching)"),
        ("EMAIL_API_KEY", "Email service API key (optional)"),
        ("GEMINI_API_KEY", "Google Gemini API key (optional, for AI features)"),
        ("OPENAI_API_KEY", "OpenAI API key (optional, AI fallback)"),
        ("FINNHUB_API_KEY", "Finnhub API key (optional, for market data)"),
        ("STRIPE_SECRET_KEY", "Stripe secret key (optional, for payments)"),
    ]
    
    results = []
    
    # Check required
    print("Checking required environment variables...")
    for var_name, description in required_vars:
        value = os.getenv(var_name) or getattr(settings, var_name.lower(), None)
        if not value:
            results.append({
                "variable": var_name,
                "status": "missing",
                "required": True,
                "description": description,
            })
            print(f"  ❌ {var_name}: MISSING - {description}")
        else:
            # Mask sensitive values
            masked = mask_value(value)
            results.append({
                "variable": var_name,
                "status": "set",
                "required": True,
                "description": description,
            })
            print(f"  ✅ {var_name}: {masked}")
    
    # Check optional
    print("\nChecking optional environment variables...")
    for var_name, description in optional_vars:
        value = os.getenv(var_name) or getattr(settings, var_name.lower(), None)
        if not value:
            results.append({
                "variable": var_name,
                "status": "not_set",
                "required": False,
                "description": description,
            })
            print(f"  ⚠️  {var_name}: NOT SET - {description}")
        else:
            masked = mask_value(value)
            results.append({
                "variable": var_name,
                "status": "set",
                "required": False,
                "description": description,
            })
            print(f"  ✅ {var_name}: {masked}")
    
    return results


def mask_value(value: str) -> str:
    """Mask sensitive values for display."""
    if not value:
        return ""
    if len(value) <= 8:
        return "***"
    return value[:4] + "***" + value[-4:]


def check_database_config() -> bool:
    """Check database configuration."""
    print("\nChecking database configuration...")
    
    db_url = settings.database_url
    if not db_url:
        print("  ❌ DATABASE_URL not set")
        return False
    
    # Check if it's a valid PostgreSQL URL
    if not db_url.startswith(("postgresql://", "postgresql+asyncpg://")):
        print(f"  ⚠️  DATABASE_URL doesn't look like PostgreSQL: {db_url[:30]}...")
        return False
    
    print("  ✅ DATABASE_URL configured")
    return True


def check_secret_key() -> bool:
    """Check secret key configuration."""
    print("\nChecking secret key...")
    
    secret_key = settings.secret_key
    if not secret_key:
        print("  ❌ SECRET_KEY not set")
        return False
    
    if len(secret_key) < 32:
        print(f"  ⚠️  SECRET_KEY is too short ({len(secret_key)} chars). Should be at least 32 characters.")
        return False
    
    if secret_key == "your-secret-key-here" or "change-me" in secret_key.lower():
        print("  ⚠️  SECRET_KEY appears to be a default/placeholder value")
        return False
    
    print("  ✅ SECRET_KEY configured")
    return True


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("TradeSignal Environment Validation")
    print("=" * 60)
    print()
    
    results = check_required_vars()
    db_ok = check_database_config()
    secret_ok = check_secret_key()
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    missing_required = [r for r in results if r["required"] and r["status"] == "missing"]
    
    if missing_required:
        print(f"❌ {len(missing_required)} required variable(s) missing:")
        for var in missing_required:
            print(f"   - {var['variable']}: {var['description']}")
        print("\n⚠️  Application may not function correctly without these variables.")
        sys.exit(1)
    else:
        print("✅ All required environment variables are set")
    
    if not db_ok or not secret_ok:
        print("⚠️  Some configuration issues detected")
        sys.exit(1)
    
    print("✅ Environment validation passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

