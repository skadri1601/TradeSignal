"""
Stock-related background tasks.
Phase 7: Celery tasks for async processing.
"""

from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='refresh_all_quotes')
def refresh_all_quotes():
    """
    Background task to refresh all stock quotes.

    This allows API endpoints to respond immediately while
    data refresh happens in the background.
    """
    try:
        from app.services.stock_price_service import StockPriceService

        # Get list of all tracked tickers (simplified for now)
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

        service = StockPriceService()
        quotes = service.get_multiple_quotes(tickers)

        logger.info(f"✅ Refreshed {len(quotes)} stock quotes")
        return {
            'status': 'success',
            'quotes_refreshed': len(quotes),
            'tickers': list(quotes.keys())
        }
    except Exception as e:
        logger.error(f"❌ Failed to refresh quotes: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='send_price_alert')
def send_price_alert(user_id: int, ticker: str, price: float, alert_type: str):
    """
    Background task to send price alert notifications.

    Args:
        user_id: User ID to send alert to
        ticker: Stock ticker
        price: Current price
        alert_type: Type of alert ('above' or 'below')
    """
    try:
        logger.info(f"📧 Sending {alert_type} alert for {ticker} @ ${price} to user {user_id}")

        # In Phase 8, this would integrate with email/push notification services
        # For now, just log the alert

        return {
            'status': 'success',
            'user_id': user_id,
            'ticker': ticker,
            'price': price,
            'alert_type': alert_type
        }
    except Exception as e:
        logger.error(f"❌ Failed to send alert: {e}")
        return {'status': 'error', 'error': str(e)}
