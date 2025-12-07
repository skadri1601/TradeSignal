"""
API routers for TradeSignal.

Import all routers here.
"""

from app.routers import trades, companies, insiders, scraper, news

__all__ = ["trades", "companies", "insiders", "scraper", "news"]
