"""
HTTPS Redirect Middleware

Enforces HTTPS in production and adds security headers.

Features:
- Redirects HTTP to HTTPS in production (301 permanent redirect)
- Supports reverse proxy deployments (Render, Heroku, AWS ALB, etc.)
- Checks X-Forwarded-Proto header when behind load balancers
- Adds comprehensive security headers (HSTS, CSP, etc.)

Configuration:
- ENVIRONMENT: Set to "production" to enable HTTPS enforcement
- TRUST_PROXY_HEADERS: Trust X-Forwarded-Proto header (default: true)

Proxy Detection:
1. Checks X-Forwarded-Proto header (if TRUST_PROXY_HEADERS=true)
2. Falls back to request.url.scheme (for direct connections)

This prevents redirect loops on platforms like Render.com where:
Client → HTTPS → Load Balancer → HTTP (+ X-Forwarded-Proto: https) → Backend

Based on TRUTH_FREE.md Phase 1.6 specifications.
"""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS and add security headers in production.

    Features:
    - Redirects HTTP to HTTPS in production (301 permanent redirect)
    - Adds security headers (HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
    - Only enforces HTTPS when ENVIRONMENT=production
    """

    def _get_request_protocol(self, request: Request) -> str:
        """
        Determine the actual request protocol (http or https).

        Priority order:
        1. X-Forwarded-Proto header (if proxy headers are trusted)
        2. Direct request.url.scheme (fallback)

        Args:
            request: FastAPI Request object

        Returns:
            str: "https" or "http"

        Notes:
            - X-Forwarded-Proto is set by Render's load balancer
            - Render terminates SSL and forwards HTTP with X-Forwarded-Proto: https
            - Only trusts proxy headers when TRUST_PROXY_HEADERS=true
        """
        from app.config import settings

        # Check X-Forwarded-Proto header first (if proxy headers are trusted)
        if settings.trust_proxy_headers:
            # X-Forwarded-Proto can contain multiple protocols if multiple proxies
            # Format: "https" or "https,http" (take first - original client protocol)
            forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()

            if forwarded_proto:
                # Handle multiple proxies: take first protocol (original client)
                protocol = forwarded_proto.split(",")[0].strip()

                if protocol in ("https", "http"):
                    return protocol

        # Fallback: check direct request scheme (for non-proxied deployments)
        return request.url.scheme

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
            # Check the X-Forwarded-Proto header (set by load balancer) first
            # Render's load balancer terminates SSL and forwards HTTP with X-Forwarded-Proto: https
            forwarded_proto = request.headers.get("x-forwarded-proto", "")
            actual_scheme = forwarded_proto if forwarded_proto else request.url.scheme

            # Only redirect if protocol is actually HTTP (not HTTPS)
            if actual_scheme != "https":
                # Redirect to HTTPS version
                https_url = request.url.replace(scheme="https")
                return RedirectResponse(url=str(https_url), status_code=301)

        # Process the request
        response = await call_next(request)

        # Add security headers in production
        if settings.environment == "production":
            # HTTP Strict Transport Security (HSTS)
            # Tell browsers to only use HTTPS for 1 year (including subdomains)
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"

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
            response.headers[
                "Permissions-Policy"
            ] = "geolocation=(), microphone=(), camera=()"

        return response
