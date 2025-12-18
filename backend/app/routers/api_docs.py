"""
API Documentation Router.

Developer portal endpoints for API documentation and SDKs.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.api_documentation_service import APIDocumentationService

router = APIRouter(prefix="/api-docs", tags=["API Documentation"])


@router.get("/openapi.json")
async def get_openapi_schema(
    app=Depends(lambda: None)  # Would inject app
):
    """Get OpenAPI schema."""
    # In production, would inject FastAPI app
    return {"message": "OpenAPI schema endpoint - implement with app injection"}


@router.get("/endpoints")
async def get_endpoints_documentation(
    db: AsyncSession = Depends(get_db),
):
    """Get all API endpoints documentation."""
    service = APIDocumentationService()
    # Would generate from actual routers
    return {
        "endpoints": [],
        "message": "Endpoint documentation - implement with router scanning",
    }


@router.get("/sdk-examples")
async def get_sdk_examples():
    """Get SDK usage examples."""
    service = APIDocumentationService()
    examples = service.generate_sdk_examples()
    return examples


@router.get("/developer-portal", response_class=HTMLResponse)
async def developer_portal():
    """Developer portal landing page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TradeSignal API - Developer Portal</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #2563eb; }
            .section { margin: 30px 0; padding: 20px; background: #f9fafb; border-radius: 8px; }
            code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
            pre { background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 8px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>TradeSignal API Developer Portal</h1>
        
        <div class="section">
            <h2>Getting Started</h2>
            <p>Welcome to the TradeSignal API. Get started by:</p>
            <ol>
                <li>Sign up for an account</li>
                <li>Generate an API key in your dashboard</li>
                <li>Start making requests</li>
            </ol>
        </div>

        <div class="section">
            <h2>Authentication</h2>
            <p>Include your API key in the Authorization header:</p>
            <pre>Authorization: Bearer YOUR_API_KEY</pre>
        </div>

        <div class="section">
            <h2>Rate Limits</h2>
            <ul>
                <li>Free: 100 requests/day</li>
                <li>Plus: 1,000 requests/day</li>
                <li>Pro: 10,000 requests/day</li>
                <li>Enterprise: Unlimited</li>
            </ul>
        </div>

        <div class="section">
            <h2>SDK Examples</h2>
            <p>See <a href="/api-docs/sdk-examples">SDK Examples</a> for code samples in Python, JavaScript, and TypeScript.</p>
        </div>

        <div class="section">
            <h2>Interactive API Docs</h2>
            <p>Visit <a href="/docs">/docs</a> for interactive Swagger documentation.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

