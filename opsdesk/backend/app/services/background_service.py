import asyncio
import logging
from datetime import datetime, timezone
from app.database.connection import SessionLocal
from app.models.incident import Incident, IncidentStatus
from app.config import settings

logger = logging.getLogger(__name__)


async def process_incident_statistics():
    """Periodic background worker task that aggregates metrics and logs telemetry."""
    interval = settings.BACKGROUND_JOB_INTERVAL_SECONDS
    logger.info(
        f"Starting background job runner with interval {interval}s",
        extra={"operation": "background_worker_start", "interval": interval}
    )

    while True:
        try:
            await asyncio.sleep(interval)
            await run_single_statistics_cycle()
        except asyncio.CancelledError:
            logger.info("Background job cancelled. Shutting down worker.")
            break
        except Exception as e:
            logger.error(
                f"Error in background statistics job: {e}",
                extra={"operation": "background_worker_error", "error": str(e)},
                exc_info=True
            )


async def run_single_statistics_cycle():
    """Executes a single iteration of background metrics processing."""
    start_time = datetime.now(timezone.utc)
    
    # Run DB query in thread pool to avoid blocking async loop
    def _do_db_work():
        with SessionLocal() as db:
            total = db.query(Incident).count()
            active = db.query(Incident).filter(
                Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS, IncidentStatus.PENDING])
            ).count()
            resolved = db.query(Incident).filter(
                Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
            ).count()
            return total, active, resolved

    total, active, resolved = await asyncio.to_thread(_do_db_work)
    duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0

    logger.info(
        f"Background job processed stats: {total} total, {active} active, {resolved} resolved (took {duration_ms:.2f}ms)",
        extra={
            "operation": "process_incident_statistics",
            "job_type": "background_worker",
            "total_incidents": total,
            "active_incidents": active,
            "resolved_incidents": resolved,
            "duration_ms": round(duration_ms, 2)
        }
    )
