import json
import logging
import sys
from typing import Any

class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in structured JSON format.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        # Check for request context tracing
        if hasattr(record, "request_id"):
            log_data["request_id"] = getattr(record, "request_id")
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# Create stream stdout handler
handler = logging.StreamHandler(sys.stdout)

# Check settings for production flag
try:
    from app.core.config import settings
    use_json = settings.ENVIRONMENT == "production"
except Exception:
    use_json = False

if use_json:
    handler.setFormatter(JSONFormatter())
else:
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

# Expose app logger instance
logger = logging.getLogger("placementor")
