import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.incident import Priority, IncidentStatus, IncidentCategory
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentStatusUpdate,
    IncidentPriorityUpdate,
    IncidentAssignUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentHistoryResponse,
)
from app.services import incident_service

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: IncidentStatus | None = Query(default=None, description="Filter by status"),
    priority: Priority | None = Query(default=None, description="Filter by priority"),
    category: IncidentCategory | None = Query(default=None, description="Filter by category"),
    search: str | None = Query(default=None, description="Search title, description, or incident #"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated list of incidents with optional filtering and search."""
    skip = (page - 1) * limit
    items, total = incident_service.get_incidents(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
        search=search,
    )
    pages = math.ceil(total / limit) if total > 0 else 1

    return IncidentListResponse(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=[IncidentResponse.model_validate(item) for item in items],
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve single incident details by ID."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    return IncidentResponse.model_validate(incident)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_new_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident ticket."""
    incident = incident_service.create_incident(db, incident_in=incident_in)
    return IncidentResponse.model_validate(incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: int, update_in: IncidentUpdate, db: Session = Depends(get_db)):
    """Update general fields of an existing incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    updated = incident_service.update_incident(db, incident=incident, update_in=update_in)
    return IncidentResponse.model_validate(updated)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    """Delete an incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    incident_service.delete_incident(db, incident=incident)
    return None


@router.put("/{incident_id}/status", response_model=IncidentResponse)
def change_status(incident_id: int, status_in: IncidentStatusUpdate, db: Session = Depends(get_db)):
    """Update status of an incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    updated = incident_service.change_incident_status(
        db,
        incident=incident,
        new_status=status_in.status,
        changed_by=status_in.changed_by
    )
    return IncidentResponse.model_validate(updated)


@router.put("/{incident_id}/priority", response_model=IncidentResponse)
def change_priority(incident_id: int, priority_in: IncidentPriorityUpdate, db: Session = Depends(get_db)):
    """Update priority of an incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    updated = incident_service.change_incident_priority(
        db,
        incident=incident,
        new_priority=priority_in.priority,
        changed_by=priority_in.changed_by
    )
    return IncidentResponse.model_validate(updated)


@router.put("/{incident_id}/assign", response_model=IncidentResponse)
def assign_technician(incident_id: int, assign_in: IncidentAssignUpdate, db: Session = Depends(get_db)):
    """Assign an incident to a technician."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    updated = incident_service.assign_incident(
        db,
        incident=incident,
        assigned_to=assign_in.assigned_to,
        changed_by=assign_in.changed_by
    )
    return IncidentResponse.model_validate(updated)


@router.get("/{incident_id}/history", response_model=list[IncidentHistoryResponse])
def get_history(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve audit and timeline history for an incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    history = incident_service.get_incident_history(db, incident_id=incident_id)
    return [IncidentHistoryResponse.model_validate(h) for h in history]
