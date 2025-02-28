from app.infastructure.repositories.notification_repository import NotificationRepository
from app.domain.entities.notifications import Notification
from typing import List, Optional

class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    

    async def create_notification(self, user_id: int, message: str, notification_type: str) -> Notification:
        notification = Notification(
            user_id=user_id,
            message=message,
            type=notification_type
        )
        
        await self.repository.save(notification=notification)
        return notification
    
    async def get_notifications(self, user_id: int) -> List[Notification]:
        return await self.repository.get_all_notifications(user_id=user_id)
    
    async def get_notification(self, user_id: int, notification_id: str) -> Optional[Notification]:
        """Fetches notification from the database."""
        return await self.repository.get_one_notification(user_id=user_id, notification_id=notification_id)

    async def mark_notifications_as_read(self, notification_id: str, user_id: int):
        """Updates database asynchronously after UI update."""
        await self.repository.mark_as_read(notification_id=notification_id, user_id=user_id)

        
    async def retry_failed_notification(self):
        print("Retrying failed notifications...")