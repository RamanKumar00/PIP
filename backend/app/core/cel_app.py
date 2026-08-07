import redis
# pyrefly: ignore [missing-import]
from celery import Celery
from app.core.config import settings

def format_redis_url(url: str) -> str:
    if not url.startswith("rediss://"):
        return url
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(url)
    # Ensure database index /0 is specified
    if not parsed.path or parsed.path == "/":
        parsed = parsed._replace(path="/0")
    rebuilt = urlunparse(parsed)
    # Ensure ssl_cert_reqs is present
    if "ssl_cert_reqs" not in rebuilt:
        separator = "&" if "?" in rebuilt else "?"
        rebuilt = f"{rebuilt}{separator}ssl_cert_reqs=none"
    return rebuilt

redis_url = format_redis_url(settings.REDIS_URL)

# Initialize Celery app instance
celery_app = Celery(
    "placementor_worker",
    broker=redis_url,
    backend=redis_url,
)

import os
is_render = os.getenv("RENDER", "false").lower() == "true"

# Configure Celery configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_always_eager=is_render or (os.getenv("CELERY_ALWAYS_EAGER", "false").lower() == "true"),
    imports=["app.worker.tasks"],  # Autoload task definitions
)
