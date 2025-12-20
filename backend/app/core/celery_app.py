"""
Celery configuration for background tasks.
Phase 7: Scalability - Background task processing.
"""

from celery import Celery
from celery.beat import PersistentScheduler
import os
import logging
import celery.schedules
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load .env file for Celery workers
# This ensures environment variables are available when Celery workers start
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file, override=True)

# Configure SQLAlchemy loggers early to reduce verbosity in Celery workers
# This prevents verbose SQL query logs from cluttering Celery output
sqlalchemy_log_level = os.getenv("SQLALCHEMY_LOG_LEVEL", "WARNING").upper()
sqlalchemy_log_level_value = getattr(logging, sqlalchemy_log_level, logging.WARNING)

# Configure all SQLAlchemy loggers to reduce noise
for logger_name in ["sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.dialects", "sqlalchemy.orm"]:
    sqlalchemy_logger = logging.getLogger(logger_name)
    sqlalchemy_logger.setLevel(sqlalchemy_log_level_value)

logger = logging.getLogger(__name__)

# Log .env file loading status
if _env_file.exists():
    logger.debug(f"Loaded .env file from {_env_file} for Celery worker")


class ResilientPersistentScheduler(PersistentScheduler):
    """
    A PersistentScheduler that automatically recovers from corrupted schedule files.
    
    This is especially useful on Windows where shelve files can become corrupted
    when the process terminates unexpectedly.
    """
    
    def setup_schedule(self):
        """
        Override setup_schedule to check for corruption and handle EOFError.
        """
        schedule_filename = getattr(self, 'schedule_filename', 'celerybeat-schedule')
        self._attempt_recovery_if_needed(schedule_filename)
        
        # Try to call parent's setup_schedule, catch corruption errors
        try:
            super().setup_schedule()
        except (EOFError, KeyError, OSError) as e:
            logger.warning(
                f"Error loading schedule file (likely corrupted): {e}. "
                "Attempting to recover by removing corrupted files."
            )
            # Clean up corrupted files
            self._cleanup_schedule_files(schedule_filename)
            # Retry setup after cleanup
            super().setup_schedule()
    
    def _attempt_recovery_if_needed(self, schedule_filename):
        """
        Check if schedule files are corrupted and attempt recovery.
        """
        schedule_path = Path(schedule_filename)
        
        # Try to detect corruption by attempting to open the shelve file
        if schedule_path.exists():
            try:
                # Try to open and read the shelve file
                import shelve
                with shelve.open(str(schedule_path), flag='r') as db:
                    _ = db.get('entries', {})
            except (EOFError, KeyError, OSError, Exception) as e:
                logger.warning(
                    f"Detected corrupted Celery Beat schedule file: {schedule_path}. "
                    f"Error: {e}. Attempting to recover by removing corrupted files."
                )
                self._cleanup_schedule_files(schedule_filename)
    
    def _cleanup_schedule_files(self, schedule_filename):
        """
        Remove all schedule files to force recreation.
        """
        schedule_path = Path(schedule_filename)
        
        # Check for common shelve file extensions
        schedule_files = [
            schedule_path,
            Path(f"{schedule_filename}.dat"),
            Path(f"{schedule_filename}.dir"),
            Path(f"{schedule_filename}.bak"),
        ]
        
        removed_count = 0
        for file_path in schedule_files:
            if file_path.exists():
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        logger.info(f"Removed corrupted schedule file: {file_path}")
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        logger.info(f"Removed corrupted schedule directory: {file_path}")
                        removed_count += 1
                except Exception as e:
                    logger.error(f"Failed to remove schedule file {file_path}: {e}")
        
        if removed_count > 0:
            logger.info(
                f"Celery Beat schedule files have been reset ({removed_count} file(s) removed). "
                "The scheduler will recreate them on next start."
            )

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

    # Enable priority queue support for SEC Form 4 processing
    task_queue_max_priority=10,
    task_default_priority=5,
    
    # Define task routes for priority queue architecture
    # Tasks will be routed to appropriate queues based on filing date
    task_routes={
        'app.tasks.sec_tasks.process_form4_document': {'queue': 'dynamic'},  # Route dynamically based on date
        'app.tasks.sec_tasks.scrape_recent_form4_filings': {'queue': 'celery'},  # Default queue
        'app.tasks.sec_tasks.scrape_all_active_companies_form4_filings': {'queue': 'celery'},  # Default queue
    },
    
    # Define queue configurations
    task_queues={
        'recent': {
            'exchange': 'celery',
            'exchange_type': 'direct',
            'routing_key': 'recent',
            'queue_arguments': {'x-max-priority': 10},
        },
        'historical': {
            'exchange': 'celery',
            'exchange_type': 'direct',
            'routing_key': 'historical',
            'queue_arguments': {'x-max-priority': 10},
        },
        'celery': {
            'exchange': 'celery',
            'exchange_type': 'direct',
            'routing_key': 'celery',
            'queue_arguments': {'x-max-priority': 10},
        },
    },
    
    # Default queue for tasks without explicit routing
    task_default_queue='celery',
    task_default_exchange='celery',
    task_default_exchange_type='direct',
    task_default_routing_key='celery',

    # Configure Celery Beat to use resilient scheduler
    beat_scheduler=ResilientPersistentScheduler,
    beat_schedule_filename=os.getenv("CELERY_BEAT_SCHEDULE_FILENAME", "celerybeat-schedule"),
    
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
        "scrape-form4-filings-every-2-hours": {
            "task": "scrape_all_active_companies_form4_filings", # A new task to iterate companies
            "schedule": celery.schedules.crontab(minute=0, hour="*/2"), # Every 2 hours
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
        # Research batch processing tasks
        "precalculate-popular-tickers-scores-daily": {
            "task": "precalculate_popular_tickers_scores",
            "schedule": celery.schedules.crontab(minute=0, hour=2),  # 2 AM UTC daily
        },
        "batch-calculate-competitive-strength-weekly": {
            "task": "batch_calculate_competitive_strength",
            "schedule": celery.schedules.crontab(minute=0, hour=3, day_of_week="sunday"),  # Sunday 3 AM UTC
        },
        "batch-calculate-management-scores-weekly": {
            "task": "batch_calculate_management_scores",
            "schedule": celery.schedules.crontab(minute=0, hour=4, day_of_week="sunday"),  # Sunday 4 AM UTC
        },
        "batch-calculate-risk-levels-daily": {
            "task": "batch_calculate_risk_levels",
            "schedule": celery.schedules.crontab(minute=0, hour=4),  # 4 AM UTC daily
        },
        # Copy Trading Automation (Phase 3)
        "sync-brokerage-accounts": {
            "task": "sync_brokerage_accounts",
            "schedule": celery.schedules.crontab(minute="*/5"),  # Every 5 minutes
        },
        "refresh-broker-tokens": {
            "task": "refresh_broker_tokens",
            "schedule": celery.schedules.crontab(hour="*/6"),  # Every 6 hours
        },
        "monitor-executed-trades": {
            "task": "monitor_executed_trades",
            "schedule": celery.schedules.crontab(minute="*/2"),  # Every 2 minutes
        },
    },
)

# Auto-discover tasks from app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])
