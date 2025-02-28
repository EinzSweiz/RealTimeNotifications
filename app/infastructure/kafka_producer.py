from confluent_kafka import Producer, Message
import json
from typing import Dict, Optional, Callable


class KafkaProducerService:
    def __init__(self):
        self.producer: Producer = Producer({
            'bootstrap.servers': 'kafka:9092',
            'client.id': 'backend-service'
        })

    def delivery_report(self, err: Optional[Exception], msg: Message) -> None:
        if err:
            print(f"❌ Message delivery failed: {err}")
        else:
            print(f"✅ Message successfully delivered!")
            print(f"  - Topic: {msg.topic()}")
            print(f"  - Partition: {msg.partition()}")
            print(f"  - Offset: {msg.offset()}")
            print(f"  - Key: {msg.key()}")
            print(f"  - Value: {msg.value()}")
    
    def send_message(self, topic: str, message: Dict) -> None:
        print(f"📤 Sending message to Kafka: {topic} -> {message}")

        self.producer.produce(
            topic,
            key=str(message.get("product_id", "default")),
            value=json.dumps(message).encode("utf-8"),
            callback=self.delivery_report
        )
        self.producer.flush()
