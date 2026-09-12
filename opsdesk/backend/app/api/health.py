import time
from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from app.config import settings
from app.database.connection import check_db_health

router = APIRouter(tags=["Health & System"])
SERVER_START_TIME = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
def liveness_check():
    """Kubernetes liveness probe: returns 200 if the process is alive."""
    return {
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.APP_NAME,
    }


@router.get("/ready")
def readiness_check(response: Response):
    """Kubernetes readiness probe: verifies database connectivity."""
    db_ok = check_db_health()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "DOWN",
            "database": "DOWN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "status": "UP",
        "database": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/system/info")
def system_info():
    """Returns detailed application and runtime environment metadata."""
    uptime_seconds = round(time.time() - SERVER_START_TIME, 2)
    db_ok = check_db_health()

    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "status": "healthy" if db_ok else "degraded",
        "database_status": "UP" if db_ok else "DOWN",
        "uptime_seconds": uptime_seconds,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "debug_mode": settings.DEBUG,
    }
