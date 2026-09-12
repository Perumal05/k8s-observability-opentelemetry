from pydantic import BaseModel
from app.schemas.incident import IncidentResponse


class DashboardSummary(BaseModel):
    total_incidents: int
    open_incidents: int
    critical_incidents: int
    resolved_incidents: int
    created_today: int
    avg_resolution_time_minutes: float | None = None
    recent_incidents: list[IncidentResponse]


class DashboardStatistics(BaseModel):
    by_priority: dict[str, int]
    by_status: dict[str, int]
    by_category: dict[str, int]
    resolution_rate_percentage: float
