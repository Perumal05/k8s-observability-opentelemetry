from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.incident import Priority, IncidentStatus, IncidentCategory
from app.schemas.user import UserResponse


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    priority: Priority = Priority.MEDIUM
    category: IncidentCategory = IncidentCategory.APPLICATION


class IncidentCreate(IncidentBase):
    reporter_id: int
    assigned_to: int | None = None


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    status: IncidentStatus | None = None
    category: IncidentCategory | None = None
    assigned_to: int | None = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus
    changed_by: int | None = None


class IncidentPriorityUpdate(BaseModel):
    priority: Priority
    changed_by: int | None = None


class IncidentAssignUpdate(BaseModel):
    assigned_to: int | None
    changed_by: int | None = None


class IncidentHistoryResponse(BaseModel):
    id: int
    incident_id: int
    action: str
    old_value: str | None = None
    new_value: str | None = None
    changed_by: int | None = None
    created_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class IncidentResponse(IncidentBase):
    id: int
    incident_number: str
    status: IncidentStatus
    reporter_id: int
    assigned_to: int | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None

    reporter: UserResponse | None = None
    assignee: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: list[IncidentResponse]
