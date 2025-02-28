import logging
import time
from confluent_kafka.admin import AdminClient, NewTopic

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = "kafka:9092"
TOPICS = [
    "notification.create",
    "notification.fetch",
    "notification.read",
]

def create_kafka_topics():
    """Create Kafka topics if they don't exist."""
    admin_client = AdminClient({"bootstrap.servers": KAFKA_BROKER})

    existing_topics = set(admin_client.list_topics(timeout=10).topics.keys())
    topics_to_create = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in TOPICS if topic not in existing_topics]

    if topics_to_create:
        logging.info(f"Creating topics: {[t.topic for t in topics_to_create]}")
        future_results = admin_client.create_topics(topics_to_create)

        for topic, future in future_results.items():
            try:
                future.result()  # Blocks until the topic is created
                logging.info(f"Topic '{topic}' created successfully.")
            except Exception as e:
                logging.error(f"Failed to create topic '{topic}': {e}")
    else:
        logging.info("All required topics already exist.")

if __name__ == "__main__":
    time.sleep(10)  # Ensure Kafka is ready
    create_kafka_topics()