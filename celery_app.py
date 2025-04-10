# project/celery_app.py
from celery import Celery
from app.core.config import Settings

celery_app = Celery(
    "tasks",
    broker=Settings.REDIS_URL,
    backend=Settings.REDIS_URL,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)