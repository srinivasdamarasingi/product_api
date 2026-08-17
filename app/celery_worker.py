from celery import Celery

celery = Celery(
    "product_api",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.celery_tasks"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=False
)