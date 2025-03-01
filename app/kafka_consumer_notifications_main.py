import asyncio
import logging
import os
from app.infastructure.consumers.kafka_consumer_notifications import KafkaNotificationConsumer
from app.services.notification_service import NotificationService
from app.infastructure.repositories.notification_repository import NotificationRepository
from app.infastructure.database import get_db


async def run_consumer():
    """Initialize and run the Kafka Consumer"""
    db = await get_db()
    repository = NotificationRepository(db=db)
    notification_service = NotificationService(repository=repository)

    consumer_group = os.getenv("CONSUMER_GROUP", "notification-consumer-group")
    kafka_consumer = KafkaNotificationConsumer(notification_service=notification_service, consumer_group=consumer_group)

    await kafka_consumer.start()  # ⬅️ Start the Kafka consumer before consuming messages
    await kafka_consumer.setup_redis()

    try:
        await kafka_consumer.consume_messages()
    except asyncio.CancelledError:
        logging.info("🛑 Kafka Consumer received shutdown signal")
    finally:
        await kafka_consumer.stop()  # ⬅️ Ensure the consumer stops properly on shutdown


if __name__ == '__main__':
    try:
        asyncio.run(run_consumer())
    except KeyboardInterrupt:
        logging.info("🛑 Kafka Consumer Interrupted, shutting down...")
