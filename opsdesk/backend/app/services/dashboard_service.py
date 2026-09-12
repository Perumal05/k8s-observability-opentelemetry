import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.incident import Incident, IncidentStatus, Priority, IncidentCategory
from app.schemas.dashboard import DashboardSummary, DashboardStatistics
from app.schemas.incident import IncidentResponse

logger = logging.getLogger(__name__)


def calculate_dashboard_summary(db: Session) -> DashboardSummary:
    """Calculate core incident metrics for the main operations dashboard."""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    total_incidents = db.query(Incident).count()
    open_incidents = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS, IncidentStatus.PENDING])
    ).count()
    critical_incidents = db.query(Incident).filter(
        Incident.priority == Priority.CRITICAL,
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS, IncidentStatus.PENDING])
    ).count()
    resolved_incidents = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
    ).count()
    created_today = db.query(Incident).filter(Incident.created_at >= today_start).count()

    # Calculate average resolution time (in minutes) for resolved incidents
    resolved_list = db.query(Incident.created_at, Incident.resolved_at).filter(
        Incident.resolved_at.isnot(None)
    ).all()

    avg_resolution_time = None
    if resolved_list:
        total_minutes = sum((res - cre).total_seconds() / 60.0 for cre, res in resolved_list if res and cre)
        avg_resolution_time = round(total_minutes / len(resolved_list), 1)

    # Fetch 5 most recent incidents
    recent_db = db.query(Incident).order_by(desc(Incident.created_at)).limit(5).all()
    recent_incidents = [IncidentResponse.model_validate(inc) for inc in recent_db]

    logger.info(
        "Calculated dashboard summary metrics",
        extra={
            "operation": "calculate_dashboard_summary",
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "critical_incidents": critical_incidents,
        }
    )

    return DashboardSummary(
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        resolved_incidents=resolved_incidents,
        created_today=created_today,
        avg_resolution_time_minutes=avg_resolution_time,
        recent_incidents=recent_incidents,
    )


def calculate_dashboard_statistics(db: Session) -> DashboardStatistics:
    """Calculate detailed aggregations by priority, status, and category."""
    # Priority breakdown
    priority_counts = dict(
        db.query(Incident.priority, func.count(Incident.id)).group_by(Incident.priority).all()
    )
    by_priority = {p.value: priority_counts.get(p, 0) for p in Priority}

    # Status breakdown
    status_counts = dict(
        db.query(Incident.status, func.count(Incident.id)).group_by(Incident.status).all()
    )
    by_status = {s.value: status_counts.get(s, 0) for s in IncidentStatus}

    # Category breakdown
    category_counts = dict(
        db.query(Incident.category, func.count(Incident.id)).group_by(Incident.category).all()
    )
    by_category = {c.value: category_counts.get(c, 0) for c in IncidentCategory}

    total = sum(by_status.values())
    resolved = by_status.get(IncidentStatus.RESOLVED.value, 0) + by_status.get(IncidentStatus.CLOSED.value, 0)
    resolution_rate = round((resolved / total * 100.0), 1) if total > 0 else 0.0

    logger.info(
        "Calculated dashboard aggregation statistics",
        extra={
            "operation": "calculate_dashboard_statistics",
            "total": total,
            "resolution_rate": resolution_rate,
        }
    )

    return DashboardStatistics(
        by_priority=by_priority,
        by_status=by_status,
        by_category=by_category,
        resolution_rate_percentage=resolution_rate,
    )
