import datetime
import redis
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/liveness", status_code=status.HTTP_200_OK)
def check_liveness() -> Any:
    """Simple API liveness indicator.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "service": "PlaceMentor AI API"
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
def check_readiness(db: Session = Depends(get_db)) -> Any:
    """Verifies that external resources (Database and Redis) are active.
    """
    # 1. Check Database connection
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_details = str(e)

    # 2. Check Redis connection
    redis_ok = False
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=1)
        r.ping()
        redis_ok = True
    except Exception as e:
        redis_details = str(e)

    if not db_ok or not redis_ok:
        err_msg = {}
        if not db_ok:
            err_msg["database"] = f"Unavailable: {db_details}"
        if not redis_ok:
            err_msg["redis"] = f"Unavailable: {redis_details}"
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unready", "failures": err_msg}
        )

    return {
        "status": "ready",
        "database": "up",
        "redis": "up",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


@router.get("/version", status_code=status.HTTP_200_OK)
def get_version() -> Any:
    """Retrieve application environment specifications.
    """
    return {
        "version": "1.0.0",
        "release_stage": "production",
        "framework": "FastAPI 0.111.0",
        "python_version": "3.12"
    }
