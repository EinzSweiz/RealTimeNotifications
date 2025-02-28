from app.domain.entities.notifications import Notification
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

class NotificationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db['notifications']

    async def save(self, notification: Notification):
        await self.collection.insert_one(notification.to_dict())
    
    async def get_all_notifications(self, user_id: int, limit: int = 100):
        data = self.collection.find({'user_id': user_id}).sort('created_at', -1).limit(limit=limit)
        data = await data.to_list(length=limit)

        return [Notification.from_dict({k: v for k, v in doc.items() if k != '_id'}) for doc in data]

    async def get_one_notification(self, user_id: int, notification_id: str) -> Optional[Notification]:
        """Fetch a single notification from MongoDB."""
        data = await self.collection.find_one({'user_id': user_id, 'notification_id': notification_id})
        if data:
            return Notification.from_dict(data)
        return None

    async def mark_as_read(self, notification_id: str, user_id: int):
        """Update the database asynchronously."""
        await self.collection.update_one(
            {'notification_id': notification_id, 'user_id': user_id},
            {'$set': {'read': True}}
        )
