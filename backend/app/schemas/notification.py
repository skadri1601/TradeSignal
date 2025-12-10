from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class NotificationBase(BaseModel):
    """
    Base schema for a notification.
    """

    user_id: int
    alert_id: Optional[int] = None
    type: str = Field(..., description="Type of notification (e.g., 'alert', 'system', 'promotion')")
    title: str = Field(..., max_length=255)
    message: str
    data: Optional[Any] = Field(None, description="Arbitrary JSON data associated with the notification")
    read: bool = False


class NotificationCreate(NotificationBase):
    """
    Schema for creating a new notification.
    """

    pass


class NotificationUpdate(BaseModel):
    """
    Schema for updating an existing notification.
    """

    read: Optional[bool] = None
    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    """
    Schema for returning a notification, including read-only fields.
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "alert_id": 456,
                "type": "alert",
                "title": "New Insider Buy Alert: NVDA",
                "message": "Nancy Pelosi bought $500K+ of NVDA stock.",
                "data": {"trade_id": 789, "ticker": "NVDA", "link": "/trades/789"},
                "read": False,
                "created_at": "2023-10-27T10:00:00.000Z",
                "updated_at": "2023-10-27T10:00:00.000Z",
                "read_at": None,
            }
        }
