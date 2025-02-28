import asyncio
from confluent_kafka import Consumer, KafkaError
import json
import logging
import time
from app.services.notification_service import NotificationService
from app.presentation.websocket.websocket_manager import WebsocketManager
from app.domain.entities.notifications import NotificationType
from app.infastructure.redis_client import redis_client
from app.infastructure.email_service import send_email_task
from app.infastructure.celery_worker import celery_app

logger = logging.getLogger(__name__)

class KafkaNotificationConsumer:
    def __init__(self, notification_service: NotificationService, consumer_group: str = 'notification-consumer-group'):
        self.notification_service = notification_service
        self.redis_pubsub = None
        self.consumer_group = consumer_group
        self.consumer = self.create_kafka_consumer_with_retry()

    def create_kafka_consumer_with_retry(self, retries: int = 5, backoff: float = 1.0) -> Consumer:
        attempt = 0
        while attempt < retries:
            try:
                logging.info(f"Attempting to connect to Kafka... (Attempt {attempt + 1})")
                consumer = Consumer({
                    'bootstrap.servers': 'kafka:9092',
                    'group.id': self.consumer_group,
                    'auto.offset.reset': 'earliest',
                    'socket.timeout.ms': 30000,
                    'enable.auto.commit': True,
                })
                consumer.subscribe([
                    "notification.create",
                    "notification.fetch",
                    "notification.read",
                ])
                logging.info("Connected to Kafka!")
                print("✅ Kafka is up!")
                return consumer
            except KafkaError as e:
                logging.error(f"Kafka connection failed: {e}")
                print(f"❌ Kafka not ready, retrying {retries}...")
                attempt += 1
                if attempt >= retries:
                    logging.error("Max retries reached. Exiting.")
                    raise e
                logging.info(f"Retrying in {backoff} seconds...")
                time.sleep(backoff)

    async def setup_redis(self):
        try:
            self.redis_pubsub = await redis_client.get_redis_pubsub()
            logger.info("Connected to Redis Pub/Sub!")
        except Exception as e:
            logger.error(f"Failed to initialize Redis Pub/Sub: {e}")

    async def consume_messages(self):
        """Consumes messages from Kafka in an infinite loop."""
        loop = asyncio.get_event_loop()
        while True:
            logger.info("Polling Kafka for new messages...")
            msg = await loop.run_in_executor(None, self.consumer.poll, 0.5)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"❌ Kafka Consumer Error: {msg.error()}")
                continue
            await self.process_message(msg)



    async def process_message(self, msg):
        """Processes a single Kafka message."""
        event = json.loads(msg.value().decode("utf-8"))
        print(f"📥 Received Kafka Event: {event}")
        logger.info(f"📥 Received Kafka Event: {event}")
        response = {}

        try:
            if msg.topic() == "notification.create":
                notification_type_enum = NotificationType(event['notification_type'])
                notification = await self.notification_service.create_notification(
                    user_id=event['user_id'],
                    message=event['message'],
                    notification_type=notification_type_enum
                )
                response = {
                    "message": "✅ Notification Created Successfully",
                    "data": notification.to_dict()
                }
                print('✅ Notification was created')
                logger.info('✅ Notificcation was created')
                 # ✅ Send Email Asynchronously with Celery
                email_subject = "New Notification"
                email_message = f"You have received a new notification: {event['message']}"
                # Inside Kafka consumer:
                print("📧 [Kafka Consumer] Sending email task to Celery")
                logging.info("📧 [Kafka Consumer] Sending email task to Celery")

                send_email_task.delay(subject=email_subject, recipient=event["user_email"], message=email_message)

                print("✅ [Kafka Consumer] Email task sent to Celery")
                logging.info("✅ [Kafka Consumer] Email task sent to Celery")



            elif msg.topic() == "notification.fetch":
                notifications = await self.notification_service.get_notifications(user_id=event['user_id'])
                response = {
                    "message": "Notifications Fetched",
                    "data": [notif.to_dict() for notif in notifications]
                }

            elif msg.topic() == "notification.read":
                print(f"🔥 Received notification.read event: {event}")  # Debugging

                user_id = event['user_id']
                notification_id = event['notification_id']

                # 1️⃣ Fetch notification from DB
                notification = await self.notification_service.get_notification(user_id, notification_id)
                if not notification:
                    print(f"❌ No notification found for user_id={user_id} and notification_id={notification_id}")
                    return  # If notification doesn't exist, do nothing

                print("🔄 Marking notification as read in DB...")  # Before DB update
                await self.notification_service.mark_notifications_as_read(notification_id=notification_id, user_id=user_id)
                print("✅ Notification marked as read!")  # After DB update

                # 2️⃣ Fetch the updated notification from DB
                notification = notification.mark_as_read()

                # 3️⃣ Send event to WebSocket (frontend gets an immediate update)
                response = {
                    "message": "Notification Marked As Read",
                    "data": notification.to_dict()
                }

                print(f"✅ Sending updated notification to WebSocket: {response}")  # Debugging



            if self.redis_pubsub:
                print(f"📡 Publishing to Redis: {response}")
                logger.info(f"📡 Publishing to Redis: {response}")

                try:
                    await self.redis_pubsub.publish('websocket_channel', json.dumps(response))
                    print(f"✅ Published to Redis Pub/Sub: {response}")
                    logger.info(f"✅ Published to Redis Pub/Sub: {response}")
                except Exception as e:
                    print(f"❌ Redis Publish Error: {e}")
                    logger.error(f"❌ Redis Publish Error: {e}")
            else:
                print("❌ Redis Pub/Sub is not initialized.")
                logger.error("❌ Redis Pub/Sub is not initialized.")


        except KafkaError as e:
            print(f"❌ Kafka Error: {e}")
            logger.error(f"❌ Kafka Error: {e}")

        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            response = {"error": f"❌ Unexpected error: {str(e)}"}
            print(f"Error during message processing: {response}")
            logger.error(f"Error during message processing: {response}")