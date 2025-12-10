from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import List, Optional

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationStorageService:
    """
    Service for managing in-app notifications in the database.
    Handles CRUD operations for Notification objects.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self, notification_data: NotificationCreate
    ) -> Notification:
        """
        Creates a new notification in the database.
        """
        notification = Notification(**notification_data.model_dump())
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_notification(self, notification_id: int) -> Optional[Notification]:
        """
        Retrieves a single notification by its ID.
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self,
        user_id: int,
        read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Notification]:
        """
        Retrieves a list of notifications for a specific user, with optional filtering by read status.
        """
        query = select(Notification).where(Notification.user_id == user_id)
        if read is not None:
            query = query.where(Notification.read == read)
        query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_user_notifications(
        self, user_id: int, read: Optional[bool] = None
    ) -> int:
        """
        Counts the number of notifications for a specific user, with optional filtering by read status.
        """
        query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        if read is not None:
            query = query.where(Notification.read == read)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() or 0

    async def update_notification(
        self, notification_id: int, update_data: NotificationUpdate
    ) -> Optional[Notification]:
        """
        Updates an existing notification's fields.
        """
        notification = await self.get_notification(notification_id)
        if not notification:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(notification, key, value)

        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_notification_as_read(
        self, notification_id: int
    ) -> Optional[Notification]:
        """
        Marks a specific notification as read.
        """
        notification = await self.get_notification(notification_id)
        if notification and not notification.read:
            notification.read = True
            notification.read_at = func.now()
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def mark_all_user_notifications_as_read(self, user_id: int) -> int:
        """
        Marks all unread notifications for a user as read.
        Returns the count of notifications updated.
        """
        result = await self.db.execute(
            select(Notification).where(
                and_(Notification.user_id == user_id, Notification.read == False)
            )
        )
        notifications_to_update = result.scalars().all()
        
        updated_count = 0
        for notification in notifications_to_update:
            notification.read = True
            notification.read_at = func.now()
            updated_count += 1
        
        if updated_count > 0:
            await self.db.commit()
        
        return updated_count

    async def delete_notification(self, notification_id: int) -> bool:
        """
        Deletes a notification by its ID.
        """
        notification = await self.get_notification(notification_id)
        if not notification:
            return False

        await self.db.delete(notification)
        await self.db.commit()
        return True

    async def delete_user_notifications(self, user_id: int) -> int:
        """
        Deletes all notifications for a specific user.
        Returns the count of notifications deleted.
        """
        query = select(Notification).where(Notification.user_id == user_id)
        result = await self.db.execute(query)
        notifications_to_delete = result.scalars().all()
        
        deleted_count = 0
        for notification in notifications_to_delete:
            await self.db.delete(notification)
            deleted_count += 1
        
        if deleted_count > 0:
            await self.db.commit()
        
        return deleted_count
