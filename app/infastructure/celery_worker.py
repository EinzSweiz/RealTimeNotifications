from celery import Celery
from app.infastructure.email_service import send_email_task
import os

celery_app = Celery(
    'tasks',
    broker="amqp://admin:admin@rabbitmq:5672/",
    backend="rpc://"
)

celery_app.conf.update(
    task_routes={"app.infastructure.email_service.send_email_task": {"queue": "email_queue"}},
    broker_connection_retry_on_startup=True
)

celery_app.task(name="app.infastructure.email_service.send_email_task")(send_email_task)
