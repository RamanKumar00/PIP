import redis
# pyrefly: ignore [missing-import]
from celery import Celery
from app.core.config import settings

# Check if Redis is running locally, otherwise fall back to synchronous eager mode
always_eager = False
try:
    r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
    r.ping()
except Exception:
    always_eager = True

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
    task_always_eager=always_eager,
    imports=["app.worker.tasks"],  # Autoload task definitions
)
