from aiokafka import AIOKafkaProducer
import json
import asyncio

class KafkaProducerService:
    def __init__(self, bootstrap_servers="kafka:9092", client_id="backend-service"):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.producer = None
        self.started = False

    async def start(self):
        if not self.started:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers, client_id=self.client_id
            )
            for attempt in range(5):
                try:
                    await self.producer.start()
                    self.started = True
                    print("✅ Connected to Kafka!")
                    return
                except Exception as e:
                    print(f"⚠️ Kafka connection attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
            print("❌ Failed to connect to Kafka after 5 attempts.")

    async def stop(self):
        if self.started and self.producer:
            await self.producer.stop()
            self.started = False

    async def send_message(self, topic: str, message: dict):
        await self.start()  # Ensure producer is started before sending a message
        print(f"📤 Sending message to Kafka: {topic} -> {message}")

        try:
            metadata = await self.producer.send_and_wait(
                topic,
                key=str(message.get("product_id", "default")).encode("utf-8"),
                value=json.dumps(message).encode("utf-8"),
            )
            print(f"✅ Message sent! Topic: {metadata.topic}, Partition: {metadata.partition}, Offset: {metadata.offset}")
        except Exception as e:
            print(f"❌ Message failed: {e}")
