"""
Observability Infrastructure.

Structured logging, application metrics, distributed tracing, centralized log aggregation.
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

active_users = Gauge(
    "active_users_total",
    "Number of active users",
)

database_queries_total = Counter(
    "database_queries_total",
    "Total database queries",
    ["operation", "table"],
)

database_query_duration_seconds = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
)

ai_api_calls_total = Counter(
    "ai_api_calls_total",
    "Total AI API calls",
    ["provider", "endpoint"],
)

ai_api_duration_seconds = Histogram(
    "ai_api_duration_seconds",
    "AI API call duration in seconds",
    ["provider"],
)

celery_tasks_total = Counter(
    "celery_tasks_total",
    "Total Celery tasks",
    ["task_name", "status"],
)

celery_task_duration_seconds = Histogram(
    "celery_task_duration_seconds",
    "Celery task duration in seconds",
    ["task_name"],
)


class StructuredLogger:
    """Structured JSON logger for production."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(self, level: str, message: str, **kwargs):
        """Log with structured JSON format."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "service": "tradesignal-backend",
            **kwargs,
        }
        self.logger.log(getattr(logging, level.upper()), json.dumps(log_entry))

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log("DEBUG", message, **kwargs)


def trace_function(operation: str, table: Optional[str] = None):
    """Decorator for tracing database operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                database_queries_total.labels(operation=operation, table=table or "unknown").inc()
                database_query_duration_seconds.labels(
                    operation=operation, table=table or "unknown"
                ).observe(duration)

                return result
            except Exception:
                duration = time.time() - start_time
                database_queries_total.labels(operation=operation, table=table or "unknown").inc()
                database_query_duration_seconds.labels(
                    operation=operation, table=table or "unknown"
                ).observe(duration)
                raise

        return wrapper
    return decorator


def trace_ai_call(provider: str):
    """Decorator for tracing AI API calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                ai_api_calls_total.labels(provider=provider, endpoint=func.__name__).inc()
                ai_api_duration_seconds.labels(provider=provider).observe(duration)

                return result
            except Exception:
                duration = time.time() - start_time
                ai_api_calls_total.labels(provider=provider, endpoint=func.__name__).inc()
                ai_api_duration_seconds.labels(provider=provider).observe(duration)
                raise

        return wrapper
    return decorator


def setup_observability(app):
    """Setup observability for FastAPI app."""
    # Setup Prometheus metrics
    Instrumentator().instrument(app).expose(app)

    # Add custom metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        from prometheus_client import generate_latest
        from fastapi.responses import Response

        return Response(
            content=generate_latest(),
            media_type="text/plain",
        )

    return app


class DistributedTracing:
    """Distributed tracing support (OpenTelemetry compatible)."""

    @staticmethod
    def create_span(operation_name: str, **attributes):
        """Create a tracing span."""
        # In production, would use OpenTelemetry
        # For now, return a simple context manager
        class Span:
            def __init__(self, name: str, attrs: Dict[str, Any]):
                self.name = name
                self.attrs = attrs
                self.start_time = time.time()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                logger = logging.getLogger(__name__)
                logger.debug(
                    f"Span {self.name} completed in {duration:.3f}s",
                    extra={"span_name": self.name, "duration": duration, **self.attrs},
                )

        return Span(operation_name, attributes)

