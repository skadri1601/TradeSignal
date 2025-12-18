"""
Celery configuration for background tasks.
Phase 7: Scalability - Background task processing.
"""

from celery import Celery
import os
import celery.schedules

# Create Celery app
celery_app = Celery(
    "tradesignal",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Configure Celery Beat schedules
    beat_schedule={
        "fetch-general-news-every-10-minutes": {
            "task": "fetch_general_news",
            "schedule": celery.schedules.crontab(minute="*/10"),
        },
        "fetch-crypto-news-every-10-minutes": {
            "task": "fetch_crypto_news",
            "schedule": celery.schedules.crontab(minute="*/10"),
        },
        "fetch-company-news-aapl-every-hour": {
            "task": "fetch_company_news",
            "schedule": celery.schedules.crontab(minute=0, hour="*"), # Every hour
            "args": ("AAPL",)
        },
        "fetch-company-news-msft-every-hour": {
            "task": "fetch_company_news",
            "schedule": celery.schedules.crontab(minute=0, hour="*"), # Every hour
            "args": ("MSFT",)
        },
        "fetch-company-news-goog-every-hour": {
            "task": "fetch_company_news",
            "schedule": celery.schedules.crontab(minute=0, hour="*"), # Every hour
            "args": ("GOOG",)
        },
        # FRED data tasks
        "fetch-current-interest-rate-every-hour": {
            "task": "fetch_current_interest_rate",
            "schedule": celery.schedules.crontab(minute=0, hour="*"), # Every hour
        },
        "fetch-rate-history-daily": {
            "task": "fetch_rate_history",
            "schedule": celery.schedules.crontab(minute=0, hour=3), # Every day at 3 AM UTC
            "args": (365,) # Fetch last 365 days
        },
        "fetch-inflation-indicator-hourly": {
            "task": "fetch_economic_indicator",
            "schedule": celery.schedules.crontab(minute=15, hour="*"), # Every hour at :15
            "args": ("inflation", "CPIAUCSL")
        },
        "fetch-unemployment-indicator-hourly": {
            "task": "fetch_economic_indicator",
            "schedule": celery.schedules.crontab(minute=30, hour="*"), # Every hour at :30
            "args": ("unemployment", "UNRATE")
        },
        "fetch-gdp-indicator-hourly": {
            "task": "fetch_economic_indicator",
            "schedule": celery.schedules.crontab(minute=45, hour="*"), # Every hour at :45
            "args": ("gdp", "GDP")
        },
        "fetch-retail-sales-indicator-hourly": {
            "task": "fetch_economic_indicator",
            "schedule": celery.schedules.crontab(minute=0, hour="*/2"), # Every 2 hours
            "args": ("retail_sales", "RSXFS")
        },
        # SEC data scraping tasks
        "scrape-form4-filings-hourly": {
            "task": "scrape_all_active_companies_form4_filings", # A new task to iterate companies
            "schedule": celery.schedules.crontab(minute=0, hour="*"), # Every hour
        },
        # Company enrichment tasks
        "enrich-all-companies-weekly": {
            "task": "enrich_all_companies_profile",
            "schedule": celery.schedules.crontab(minute=0, hour=0, day_of_week="sunday"), # Weekly on Sunday midnight
        },
        # Pattern analysis tasks
        "analyze-all-active-companies-daily": {
            "task": "analyze_all_active_companies_patterns",
            "schedule": celery.schedules.crontab(minute=0, hour=2), # Daily at 2 AM UTC
        },
        "precompute-top-patterns-every-6-hours": {
            "task": "precompute_top_patterns",
            "schedule": celery.schedules.crontab(minute=30, hour="*/6"), # Every 6 hours at :30
        },
        # AI Insights tasks
        "generate-daily-ai-summary": {
            "task": "generate_daily_ai_summary",
            "schedule": celery.schedules.crontab(minute=0, hour=11), # 6 AM EST = 11 AM UTC
        },
        # IVT tasks
        "batch-process-ivt-calculations": {
            "task": "batch_process_ivt_calculations",
            "schedule": celery.schedules.crontab(minute=0, hour=3), # 3 AM UTC (nightly)
        },
        # TS Score tasks
        "batch-update-ts-scores": {
            "task": "batch_update_ts_scores",
            "schedule": celery.schedules.crontab(minute=0, hour="*/6"), # Every 6 hours
        },
    },
)

# Auto-discover tasks from app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])
