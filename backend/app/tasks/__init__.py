"""Background tasks for TradeSignal."""

from app.tasks.stock_tasks import refresh_all_quotes, send_price_alert
from app.tasks.news_tasks import fetch_general_news_task, fetch_crypto_news_task, fetch_company_news_task
from app.tasks.sec_tasks import update_cik_for_company_task, scrape_recent_form4_filings, process_form4_document_task, scrape_all_active_companies_form4_filings_task
from app.tasks.alert_tasks import send_discord_alert_task, send_slack_alert_task, send_sms_alert_task, create_in_app_notification_task, \
    send_webhook_notification_task, send_test_webhook_notification_task, send_email_notification_task, \
    send_subscription_confirmation_email_task, send_test_email_notification_task, send_push_notification_task, send_test_push_notification_task
from app.tasks.enrichment_tasks import enrich_company_profile_task, enrich_all_companies_profile_task
# REMOVED: Broken tasks that depend on deleted PatternAnalysisService
# from app.tasks.analysis_tasks import analyze_company_patterns_task, analyze_all_active_companies_patterns_task, precompute_top_patterns_task
from app.tasks.ai_tasks import generate_daily_ai_summary_task, cache_ai_insights_task
from app.tasks.ivt_tasks import calculate_ivt_for_company_task, batch_process_ivt_calculations_task
from app.tasks.ts_score_tasks import calculate_ts_score_for_company_task, batch_update_ts_scores_task
from app.tasks.marketing_tasks import send_campaign_email_task, process_drip_campaign_task
from app.tasks.copy_trade_tasks import (
    execute_copy_trade_task,
    check_and_execute_copy_trades_task,
    sync_brokerage_accounts_task,
    refresh_broker_tokens_task,
    monitor_executed_trades_task,
)

__all__ = [
    "refresh_all_quotes",
    "send_price_alert",
    "fetch_general_news_task",
    "fetch_crypto_news_task",
    "fetch_company_news_task",
    "update_cik_for_company_task",
    "scrape_recent_form4_filings",
    "process_form4_document_task",
    "scrape_all_active_companies_form4_filings_task",
    "send_discord_alert_task",
    "send_slack_alert_task",
    "send_sms_alert_task",
    "create_in_app_notification_task",
    "send_webhook_notification_task",
    "send_test_webhook_notification_task",
    "send_email_notification_task",
    "send_subscription_confirmation_email_task",
    "send_test_email_notification_task",
    "send_push_notification_task",
    "send_test_push_notification_task",
    "enrich_company_profile_task",
    "enrich_all_companies_profile_task",
    # REMOVED: Broken tasks - "analyze_company_patterns_task", "analyze_all_active_companies_patterns_task", "precompute_top_patterns_task"
    "generate_daily_ai_summary_task",
    "cache_ai_insights_task",
    "calculate_ivt_for_company_task",
    "batch_process_ivt_calculations_task",
    "calculate_ts_score_for_company_task",
    "batch_update_ts_scores_task",
    "send_campaign_email_task",
    "process_drip_campaign_task",
    "execute_copy_trade_task",
    "check_and_execute_copy_trades_task",
    "sync_brokerage_accounts_task",
    "refresh_broker_tokens_task",
    "monitor_executed_trades_task",
]
