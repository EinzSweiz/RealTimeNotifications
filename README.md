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
    participant WebSocket as WebSocket Client
    participant FastAPI as FastAPI Server
    participant Kafka as Kafka Broker
    participant Redis as Redis Pub/Sub
    participant MongoDB as MongoDB
    participant Celery as Celery Worker
    participant Email as Email Service

    WebSocket ->> FastAPI: Send Notification Event
    FastAPI ->> Kafka: Publish Event
    Kafka ->> Consumer: Consume Event
    Consumer ->> MongoDB: Store Notification
    Consumer ->> Redis: Publish WebSocket Update
    Consumer ->> Celery: Trigger Email Notification
    Celery ->> Email: Send Email
    Redis ->> WebSocket: Push Notification Update


🚀 How to Run the Project Locally

1️⃣ Clone the repository

git clone https://github.com/yourusername/event-driven-notifications.git
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

🛠 Running Tests

pytest tests/ or make test(Makefile automatization)
This will run unit tests for WebSocket, Kafka consumers, and DDD entities.

📊 Future Improvements

✅ Prometheus + Grafana for monitoring 📊
✅ Add authentication & user management 🔒
✅ Deploy to AWS using Terraform & Kubernetes ☁️

💡 Contributing

If you’d like to improve this project, feel free to fork & submit a PR!

🏆 Author

👨‍💻 [Riad Sultanov] – Email: riad.sultanov.1999@gmail.com

🚀 Feel free to star ⭐ this repository if you find it useful!
