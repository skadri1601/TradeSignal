"""
API routers for TradeSignal.

Import all routers here.
"""

from app.routers import (
    auth,
    trades,
    companies,
    insiders,
    scraper,
    scheduler,
    push,
    stocks,
    health,
    congressional_trades,
    congresspeople,
    billing,
    fed,
    orders,
    admin,
    contact,
    jobs,
    news,
    public_contact,
    data_health,
    notifications,
    ai,
    # REMOVED: patterns (file was deleted by Gemini along with pattern_analysis_service)
    tickets,
    alerts,
)

__all__ = [
    "auth",
    "trades",
    "companies",
    "insiders",
    "scraper",
    "scheduler",
    "push",
    "stocks",
    "health",
    "congressional_trades",
    "congresspeople",
    "billing",
    "fed",
    "orders",
    "admin",
    "contact",
    "jobs",
    "news",
    "public_contact",
    "data_health",
    "notifications",
    "ai",
    # REMOVED: "patterns" (file was deleted by Gemini)
    "tickets",
    "alerts",
]
