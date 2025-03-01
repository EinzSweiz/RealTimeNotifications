📡 Event-Driven Notification Microservice

🚀 Overview

This microservice provides real-time notifications using WebSockets, Kafka, Redis, Celery, and RabbitMQ.
It allows users to receive instant updates via WebSockets while ensuring event-driven processing for creating, fetching, and reading notifications.

🌟 Key Features

WebSocket-based real-time notifications 📡

Event-driven architecture using Kafka 🎯

Asynchronous task execution with Celery & RabbitMQ ⚡

Redis Pub/Sub for WebSocket updates 🚀

MongoDB for notification storage 📂

Email notifications using Celery 📧

Fully Dockerized with docker-compose 🐳

🎯 System Architecture
sequenceDiagram
    participant Frontend as WebSocket Client
    participant FastAPI as WebSocket Server
    participant KafkaProducer as Kafka Producer
    participant Kafka as Kafka Broker
    participant KafkaConsumer as Kafka Consumer
    participant Redis as Redis Pub/Sub
    participant MongoDB as MongoDB
    participant Celery as Celery Worker
    participant Email as Email Service
    participant Prometheus as Metrics Collector
    participant Grafana as Monitoring Dashboard

    Frontend ->> FastAPI: Send Notification Event
    FastAPI ->> KafkaProducer: Forward Event to Kafka
    KafkaProducer ->> Kafka: Publish Event

    Kafka ->> KafkaConsumer: Consumer Reads Event
    KafkaConsumer ->> MongoDB: Store Notification
    KafkaConsumer ->> Redis: Publish WebSocket Update
    KafkaConsumer ->> Celery: Trigger Email Notification

    Celery ->> Email: Send Email

    Redis ->> FastAPI: Push WebSocket Update
    FastAPI ->> Frontend: Send Notification to Client

    KafkaConsumer ->> Prometheus: Expose Kafka Metrics
    Redis ->> Prometheus: Expose Redis Metrics
    Prometheus ->> Grafana: Provide Monitoring Data


🚀 How to Run the Project Locally

1️⃣ Clone the repository

git clone https://github.com/EinzSweiz/RealTimeNotifications.git
cd event-driven-notifications
docker-compose up --build  # or use Makefile automation

📡 WebSocket API Usage

🔌 Connecting to WebSocket

ws://localhost:8002/ws/{user_id}

📩 Sending Events

1️⃣ Create Notification
{
  "type": "notification",
  "event": "create",
  "message": "Your application was rejected",
  "notification_type": "proposal_rejected",
  "user_email": "user@example.com"
}

2️⃣ Fetch Notifications

{
  "type": "notification",
  "event": "fetch"
}


3️⃣ Mark Notification as Read

{
  "type": "notification",
  "event": "read",
  "notification_id": "some-uuid"
}

📊 Monitoring with Prometheus & Grafana
🔹 How We Collect Metrics

We implemented custom exporters for:

    Kafka Exporter → Collects Kafka consumer lag, partition offsets, and message rates.
    Redis Exporter → Tracks Pub/Sub events, cache hits/misses, and WebSocket updates.
    WebSocket Metrics → Monitors active connections and message flow.
    Celery Exporter → Measures task execution time and queue performance.
2️⃣ Access Prometheus Metrics

    Prometheus UI → http://localhost:9090
    
    To query specific metrics, use:
    up
    kafka_messages_total
    redis_pubsub_messages
    celery_task_duration_seconds
    websocket_active_connections
3️⃣ Access Grafana Dashboard

    Grafana UI → http://localhost:3000
    Default login:
        Username: admin
        Password: admin
    Add Prometheus as a data source in Grafana.
    
🛠 Running Tests

pytest tests/ or make test(Makefile automatization)
This will run unit tests for WebSocket, Kafka consumers, and DDD entities.

📊 Future Improvements

    Prometheus + Grafana for monitoring 📊 (DONE ✅)
    Add authentication & user management 🔒
    Deploy to AWS using EC2 ☁️
    
4️⃣ Available Metrics

    Kafka Events Processed: kafka_messages_total
    Redis WebSocket Updates: redis_pubsub_messages
    Celery Task Execution Time: celery_task_duration_seconds
    WebSocket Active Connections: websocket_active_connections

💡 Contributing

If you’d like to improve this project, feel free to fork & submit a PR!

🏆 Author

👨‍💻 [Riad Sultanov] – Email: riad.sultanov.1999@gmail.com

🚀 Feel free to star ⭐ this repository if you find it useful!
