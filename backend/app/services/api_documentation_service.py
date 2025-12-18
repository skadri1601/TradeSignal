"""
API Documentation Service.

Generates comprehensive API documentation and developer portal content.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi

logger = logging.getLogger(__name__)


class APIDocumentationService:
    """Service for generating API documentation."""

    @staticmethod
    def generate_openapi_schema(app) -> Dict[str, Any]:
        """Generate OpenAPI schema for the application."""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="TradeSignal API",
            version="1.0.0",
            description="""
            TradeSignal API - Real-time insider trading intelligence platform.

            ## Features

            - **Insider Trading Data**: Access real-time SEC Form 4 filings
            - **Congressional Trades**: Track politician stock transactions
            - **AI Insights**: Get AI-powered analysis and recommendations
            - **Portfolio Analysis**: Virtual portfolio tracking and analysis
            - **Advanced Alerts**: Complex query-based alert system
            - **Enterprise API**: Programmatic access for institutional clients

            ## Authentication

            Most endpoints require authentication via JWT token.
            Include the token in the Authorization header:

            ```
            Authorization: Bearer <your_token>
            ```

            ## Rate Limits

            Rate limits vary by subscription tier:
            - Free: 100 requests/day
            - Plus: 1,000 requests/day
            - Pro: 10,000 requests/day
            - Enterprise: Unlimited

            ## Webhooks

            Enterprise tier supports webhooks for real-time notifications.
            Configure webhooks in the Enterprise API section.

            ## Support

            For API support, contact: api@tradesignal.com
            """,
            routes=app.routes,
        )

        # Add custom OpenAPI extensions
        openapi_schema["info"]["x-logo"] = {
            "url": "https://tradesignal.com/logo.png"
        }

        # Add server information
        openapi_schema["servers"] = [
            {
                "url": "https://api.tradesignal.com/v1",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.tradesignal.com/v1",
                "description": "Staging server"
            }
        ]

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            "APIKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
            }
        }

        app.openapi_schema = openapi_schema
        return openapi_schema

    @staticmethod
    def generate_endpoint_documentation(router: APIRouter) -> List[Dict[str, Any]]:
        """Generate documentation for all endpoints in a router."""
        endpoints = []

        for route in router.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                endpoint_info = {
                    "path": route.path,
                    "methods": list(route.methods),
                    "summary": getattr(route, "summary", ""),
                    "description": getattr(route, "description", ""),
                    "tags": getattr(route, "tags", []),
                }

                # Get response models
                if hasattr(route, "response_model"):
                    endpoint_info["response_model"] = str(route.response_model)

                endpoints.append(endpoint_info)

        return endpoints

    @staticmethod
    def generate_sdk_examples() -> Dict[str, str]:
        """Generate SDK usage examples."""
        return {
            "python": """
# Python SDK Example
import requests

headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

# Get insider trades
response = requests.get(
    "https://api.tradesignal.com/v1/trades",
    headers=headers,
    params={"ticker": "AAPL", "days_back": 30}
)

trades = response.json()
print(f"Found {len(trades)} trades")
            """,
            "javascript": """
// JavaScript SDK Example
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://api.tradesignal.com/v1',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});

// Get insider trades
client.get('/trades', {
  params: { ticker: 'AAPL', days_back: 30 }
})
.then(response => {
  console.log(`Found ${response.data.length} trades`);
})
.catch(error => {
  console.error('Error:', error);
});
            """,
            "typescript": """
// TypeScript SDK Example
import axios from 'axios';

interface Trade {
  id: number;
  ticker: string;
  insider_name: string;
  transaction_type: string;
  shares: number;
  total_value: number;
}

const client = axios.create({
  baseURL: 'https://api.tradesignal.com/v1',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});

async function getTrades(ticker: string): Promise<Trade[]> {
  const response = await client.get<Trade[]>('/trades', {
    params: { ticker, days_back: 30 }
  });
  return response.data;
}

getTrades('AAPL').then(trades => {
  console.log(`Found ${trades.length} trades`);
});
            """,
        }

