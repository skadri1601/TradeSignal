from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.alert import AlertResponse, AlertHistoryResponse

class AlertDebugResponse(BaseModel):
    """
    Schema for detailed alert debugging information.
    """
    alert: AlertResponse
    recent_history: List[AlertHistoryResponse]
    # Potentially add more debug info here in the future
    # e.g., "dry_run_results": Optional[Dict]
    # e.g., "next_check_time": Optional[datetime]
