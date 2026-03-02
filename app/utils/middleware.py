"""
Custom middleware for the application
"""
import time
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        # Generate request ID
        request_id = request.headers.get("X-Request-ID", str(time.time()))

        # Log request
        logger.info(f"Request started: {request.method} {request.url.path} [ID: {request_id}]")

        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[ID: {request_id}] - Status: {response.status_code} - Time: {process_time:.3f}s"
            )

            return response

        except Exception as e:
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[ID: {request_id}] - Error: {str(e)}"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""

    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records = defaultdict(list)
        self.cleanup_task = None

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for certain paths
        if request.url.path.startswith("/static") or request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Clean old records
        now = datetime.now()
        self.rate_limit_records[client_ip] = [
            record for record in self.rate_limit_records[client_ip]
            if record > now - timedelta(seconds=settings.RATE_LIMIT_PERIOD)
        ]

        # Check rate limit
        if len(self.rate_limit_records[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")

        # Add current request
        self.rate_limit_records[client_ip].append(now)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        csp = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp)

        return response