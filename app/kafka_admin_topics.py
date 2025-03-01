import logging
import asyncio
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = "kafka:9092"
TOPICS = [
    "notification.create",
    "notification.fetch",
    "notification.read",
]

async def create_kafka_topics(max_attempts: int = 5, max_delay: int = 5):
    """Create Kafka topics if they don't exist."""

    admin_client = AIOKafkaAdminClient(bootstrap_servers=KAFKA_BROKER)

    for attempt in range(max_attempts):
        try:
            await admin_client.start()  # Start only once outside the loop
            await admin_client.list_topics()  # Check connection
            logging.info(f"Connected to Kafka (Attempt {attempt+1}/{max_attempts})")
            break  # Exit the loop once Kafka is reachable
        except Exception as e:
            logging.warning(f"Kafka connection failed (Attempt {attempt+1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(max_delay)
            else:
                logging.error(f"Failed to connect to Kafka after {max_attempts} attempts.")
                await admin_client.close()  # Ensure cleanup
                raise e  # Stop execution if Kafka is still unreachable

    try:
        existing_topics = set(await admin_client.list_topics())  # Await the async call
        topics_to_create = [
            NewTopic(topic, num_partitions=1, replication_factor=1)
            for topic in TOPICS if topic not in existing_topics
        ]

        if topics_to_create:
            logging.info(f"Creating topics: {[t.name for t in topics_to_create]}")
            await admin_client.create_topics(topics_to_create)  # Await the async call
            logging.info("Topics created successfully.")
        else:
            logging.info("All required topics already exist.")

    except Exception as e:
        logging.error(f"Error while creating Kafka topics: {e}")

    finally:
        await admin_client.close()  # Ensure cleanup

if __name__ == "__main__":
    asyncio.run(create_kafka_topics())
