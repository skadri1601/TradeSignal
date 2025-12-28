"""
Background Tasks API Endpoints.
NOTE: Celery removed - these endpoints return disabled status.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


@router.post("/stocks/refresh")
async def trigger_stock_refresh() -> Dict[str, Any]:
    """
    Trigger background stock quote refresh.
    NOTE: Celery tasks have been removed.
    """
    return {
        "task_id": None,
        "status": "disabled",
        "message": "Background tasks are currently disabled. Stock data is fetched on-demand.",
    }


@router.post("/alerts/send")
async def trigger_price_alert(
    user_id: int, ticker: str, price: float, alert_type: str = "above"
) -> Dict[str, Any]:
    """
    Trigger background price alert notification.
    NOTE: Celery tasks have been removed.
    """
    return {
        "task_id": None,
        "status": "disabled",
        "message": "Background tasks are currently disabled. Alerts are processed on-demand.",
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a background task.
    NOTE: Celery tasks have been removed.
    """
    return {
        "task_id": task_id,
        "status": "disabled",
        "result": None,
        "info": "Background tasks are currently disabled.",
    }
