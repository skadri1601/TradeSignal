import sys
import os
import asyncio

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Mock environment variables if needed
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
os.environ["JWT_SECRET"] = "secret" * 5

try:
    from app.main import app
    print("Successfully imported app")
    
    print("\nRegistered Routes:")
    for route in app.routes:
        if hasattr(route, "path"):
            methods = ",".join(route.methods) if hasattr(route, "methods") else "N/A"
            print(f" - {route.path} [{methods}]")
            
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
