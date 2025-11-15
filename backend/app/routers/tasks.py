"""
Background Tasks API Endpoints.
Phase 7: Scalability - Async task management.
"""

from fastapi import APIRouter, HTTPException
from app.tasks.stock_tasks import refresh_all_quotes, send_price_alert
from typing import Dict, Any

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


@router.post("/stocks/refresh")
async def trigger_stock_refresh() -> Dict[str, Any]:
    """
    Trigger background stock quote refresh.

    Returns immediately while processing happens asynchronously.
    Use task_id to check status via Flower UI at http://localhost:5555

    Returns:
        dict: Task ID and status
    """
    try:
        task = refresh_all_quotes.delay()
        return {
            "task_id": str(task.id),
            "status": "queued",
            "message": "Stock refresh task queued. Check progress at http://localhost:5555",
            "flower_url": f"http://localhost:5555/task/{task.id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue task: {str(e)}"
        )


@router.post("/alerts/send")
async def trigger_price_alert(
    user_id: int,
    ticker: str,
    price: float,
    alert_type: str = "above"
) -> Dict[str, Any]:
    """
    Trigger background price alert notification.

    Args:
        user_id: User ID to notify
        ticker: Stock ticker symbol
        price: Price threshold
        alert_type: 'above' or 'below'

    Returns:
        dict: Task ID and status
    """
    try:
        task = send_price_alert.delay(user_id, ticker, price, alert_type)
        return {
            "task_id": str(task.id),
            "status": "queued",
            "message": f"Alert task queued for {ticker} @ ${price}",
            "flower_url": f"http://localhost:5555/task/{task.id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue alert: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a background task.

    Args:
        task_id: Task ID returned from POST endpoints

    Returns:
        dict: Task status and result
    """
    try:
        from celery.result import AsyncResult

        task = AsyncResult(task_id)

        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "info": task.info if task.status == "FAILURE" else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )
