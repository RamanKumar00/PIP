from celery import Celery
from app.core.config import settings

# Initialize Celery app instance
celery_app = Celery(
    "placementor_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    imports=["app.worker.tasks"],  # Autoload task definitions
)
