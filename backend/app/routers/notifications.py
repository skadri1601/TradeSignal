from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.services.notification_storage_service import NotificationStorageService
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.schemas.common import PaginatedResponse
from app.models.user import User
from app.core.security import get_current_active_user


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a list of notifications for the current user.
    """
    service = NotificationStorageService(db)
    skip = (page - 1) * limit
    notifications = await service.get_user_notifications(
        user_id=current_user.id, read=read, skip=skip, limit=limit
    )
    total = await service.count_user_notifications(user_id=current_user.id, read=read)

    return PaginatedResponse.create(
        items=notifications, total=total, page=page, limit=limit
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single notification by its ID.
    """
    service = NotificationStorageService(db)
    notification = await service.get_notification(notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    return notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a notification (e.g., mark as read).
    """
    service = NotificationStorageService(db)
    notification = await service.get_notification(notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    updated_notification = await service.update_notification(notification_id, notification_update)
    
    if not updated_notification:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update notification")
    
    return updated_notification


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a specific notification as read.
    """
    service = NotificationStorageService(db)
    notification = await service.get_notification(notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    read_notification = await service.mark_notification_as_read(notification_id)
    
    if not read_notification:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark notification as read")
    
    return read_notification


@router.post("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark all unread notifications for the current user as read.
    """
    service = NotificationStorageService(db)
    updated_count = await service.mark_all_user_notifications_as_read(current_user.id)
    return {"message": f"Successfully marked {updated_count} notifications as read."}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific notification.
    """
    service = NotificationStorageService(db)
    notification = await service.get_notification(notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found or unauthorized")
    
    deleted = await service.delete_notification(notification_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete notification")
    
    return {"message": "Notification deleted successfully"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_user_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete all notifications for the current user.
    """
    service = NotificationStorageService(db)
    deleted_count = await service.delete_user_notifications(current_user.id)
    return {"message": f"Successfully deleted {deleted_count} notifications."}
