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
    congressional_trades,
    congresspeople,
    billing,
    orders,
    admin,
    contact,
    jobs,
    news,
    public_contact,
    data_health,
    notifications,
    ai,
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
    "congressional_trades",
    "congresspeople",
    "billing",
    "orders",
    "admin",
    "contact",
    "jobs",
    "news",
    "public_contact",
    "data_health",
    "notifications",
    "ai",
    "tickets",
    "alerts",
]
