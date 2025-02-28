import asyncio
import logging
import os
from app.infastructure.consumers.kafka_consumer_notifications import KafkaNotificationConsumer
from app.services.notification_service import NotificationService
from app.infastructure.repositories.notification_repository import NotificationRepository
from app.infastructure.database import get_db


async def run_consumer():

    db = await get_db()
    repository = NotificationRepository(db=db)
    notification_service = NotificationService(repository=repository)

    consumer_group = os.getenv("CONSUMER_GROUP", "notification-consumer-group")

    kafka_consumer = KafkaNotificationConsumer(notification_service=notification_service, consumer_group=consumer_group)
    await kafka_consumer.setup_redis()
    await kafka_consumer.consume_messages()

if __name__ == '__main__':
    asyncio.run(run_consumer())