"""
HTTPS Redirect Middleware

Enforces HTTPS in production and adds security headers.
Based on TRUTH_FREE.md Phase 1.6 specifications.
"""

import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS and add security headers in production.

    Features:
    - Redirects HTTP to HTTPS in production (301 permanent redirect)
    - Adds security headers (HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
    - Only enforces HTTPS when ENVIRONMENT=production
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process each request.

        In production:
        - Redirect HTTP -> HTTPS with 301 status
        - Add security headers to all responses

        In development:
        - Pass through without modification
        """
        # Get environment from config
        from app.config import settings

        # Only enforce HTTPS in production
        if settings.environment == "production":
            # Check if request is HTTP (not HTTPS)
            if request.url.scheme != "https":
                # Redirect to HTTPS version
                https_url = request.url.replace(scheme="https")
                return RedirectResponse(url=str(https_url), status_code=301)

        # Process the request
        response = await call_next(request)

        # Add security headers in production
        if settings.environment == "production":
            # HTTP Strict Transport Security (HSTS)
            # Tell browsers to only use HTTPS for 1 year (including subdomains)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

            # Prevent MIME type sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"

            # Prevent clickjacking attacks
            response.headers["X-Frame-Options"] = "DENY"

            # Enable XSS protection (legacy browsers)
            response.headers["X-XSS-Protection"] = "1; mode=block"

            # Content Security Policy (basic)
            response.headers["Content-Security-Policy"] = "default-src 'self'"

            # Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Permissions Policy (disable unnecessary features)
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
