import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from app.services.notification_service import NotificationService
from app.presentation.websocket.websocket_manager import WebsocketManager
from app.domain.entities.notifications import NotificationType
from app.infastructure.repositories.redis_repository import redis_repository
from app.infastructure.email_service import send_email_task
from app.infastructure.celery_worker import celery_app


logger = logging.getLogger(__name__)


class KafkaNotificationConsumer:
    def __init__(self, notification_service: NotificationService, consumer_group: str = 'notification-consumer-group'):
        self.notification_service = notification_service
        self.redis_pubsub = None
        self.consumer_group = consumer_group
        self.consumer = None

    async def start(self, max_retries:int=5, max_delay:int=5):
        """Start the Kafka consumer asynchronously"""

        self.consumer = AIOKafkaConsumer(
            "notification.create",
            "notification.fetch",
            "notification.read",
            bootstrap_servers="kafka:9092",
            group_id=self.consumer_group,
            auto_offset_reset="earliest"
        )
        for attempt in range(max_retries):
            try:
                await self.consumer.start()
                logging.info(f"�� Kafka Consumer started (Attempt {attempt+1}/{max_retries})")
                return
            except Exception as e:
                logging.error(f"�� Failed to start Kafka Consumer (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(max_delay)  # Wait before retrying
                else:
                    logging.error(f"Failed to start Kafka Consumer")
                    raise e

    async def stop(self):
        """Shutdown Kafka consumer"""
        if self.consumer:
            await self.consumer.stop()
            logging.info("🛑 Kafka Consumer Stopped")

    async def setup_redis(self):
        """Initialize Redis Pub/Sub"""
        try:
            self.redis_pubsub = await redis_repository.get_redis_pubsub()
            logger.info("✅ Connected to Redis Pub/Sub!")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis Pub/Sub: {e}")

    async def consume_messages(self):
        """Consume messages asynchronously from Kafka"""
        try:
            async for msg in self.consumer:
                await self.process_message(msg)
        except Exception as e:
            logger.error(f"❌ Kafka Consumer Error: {e}")
        finally:
            await self.stop()  # Ensure shutdown when an error occurs

    async def process_message(self, msg):
        """Process a single Kafka message"""
        try:
            event = json.loads(msg.value.decode("utf-8"))
            print(f"📥 Received Kafka Event: {event}")
            logger.info(f"📥 Received Kafka Event: {event}")
            response = {}

            if msg.topic == "notification.create":
                notification_type_enum = NotificationType(event["notification_type"])
                notification = await self.notification_service.create_notification(
                    user_id=event["user_id"],
                    message=event["message"],
                    notification_type=notification_type_enum,
                )
                response = {
                    "message": "✅ Notification Created Successfully",
                    "data": notification.to_dict(),
                }

                # ✅ Send Email Asynchronously with Celery
                email_subject = "New Notification"
                email_message = f"You have received a new notification: {event['message']}"
                print("📧 [Kafka Consumer] Sending email task to Celery")
                send_email_task.delay(subject=email_subject, recipient=event["user_email"], message=email_message)

            elif msg.topic == "notification.fetch":
                notifications = await self.notification_service.get_notifications(user_id=event["user_id"])
                response = {
                    "message": "Notifications Fetched",
                    "data": [notif.to_dict() for notif in notifications],
                }

            elif msg.topic == "notification.read":
                user_id = event["user_id"]
                notification_id = event["notification_id"]

                notification = await self.notification_service.get_notification(user_id, notification_id)
                if not notification:
                    print(f"❌ No notification found for user_id={user_id} and notification_id={notification_id}")
                    return

                await self.notification_service.mark_notifications_as_read(notification_id=notification_id, user_id=user_id)
                notification = notification.mark_as_read()

                response = {
                    "message": "Notification Marked As Read",
                    "data": notification.to_dict(),
                }

            # ✅ Publish to Redis (for WebSocket notification)
            if self.redis_pubsub:
                try:
                    await self.redis_pubsub.publish("websocket_channel", json.dumps(response))
                    print(f"✅ Published to Redis Pub/Sub: {response}")
                except Exception as e:
                    print(f"❌ Redis Publish Error: {e}")
            else:
                print("❌ Redis Pub/Sub is not initialized.")

        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            print(f"❌ Unexpected error: {str(e)}")


async def run_consumer():
    """Entry point for Kafka Consumer Service"""
    notification_service = NotificationService()
    kafka_consumer = KafkaNotificationConsumer(notification_service=notification_service)
    await kafka_consumer.start()
    await kafka_consumer.setup_redis()
    await kafka_consumer.consume_messages()


if __name__ == "__main__":
    asyncio.run(run_consumer())
