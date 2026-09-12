import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.models.incident import Incident, IncidentHistory, IncidentStatus, Priority, IncidentCategory
from app.models.comment import Comment
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate

logger = logging.getLogger(__name__)


def generate_incident_number(db: Session) -> str:
    """Generate a unique sequential incident number, e.g., INC-1006."""
    last_incident = db.query(Incident).order_by(desc(Incident.id)).first()
    next_id = (last_incident.id + 1) if last_incident else 1
    return f"INC-{1000 + next_id}"


def get_incidents(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: IncidentStatus | None = None,
    priority: Priority | None = None,
    category: IncidentCategory | None = None,
    search: str | None = None
) -> tuple[list[Incident], int]:
    """Search and filter incidents with pagination."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if priority:
        query = query.filter(Incident.priority == priority)
    if category:
        query = query.filter(Incident.category == category)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Incident.title.ilike(search_pattern),
                Incident.description.ilike(search_pattern),
                Incident.incident_number.ilike(search_pattern),
            )
        )

    total = query.count()
    items = query.order_by(desc(Incident.created_at)).offset(skip).limit(limit).all()

    logger.info(
        f"Fetched {len(items)} incidents (total matching: {total})",
        extra={"operation": "search_incidents", "count": len(items), "total": total}
    )
    return items, total


def get_incident_by_id(db: Session, incident_id: int) -> Incident | None:
    """Retrieve single incident by ID."""
    return db.query(Incident).filter(Incident.id == incident_id).first()


def create_incident(db: Session, incident_in: IncidentCreate) -> Incident:
    """Create a new incident and record initial creation history."""
    incident_number = generate_incident_number(db)
    now = datetime.now(timezone.utc)

    incident = Incident(
        incident_number=incident_number,
        title=incident_in.title,
        description=incident_in.description,
        priority=incident_in.priority,
        status=IncidentStatus.OPEN,
        category=incident_in.category,
        reporter_id=incident_in.reporter_id,
        assigned_to=incident_in.assigned_to,
        created_at=now,
        updated_at=now,
    )
    db.add(incident)
    db.flush()

    # Record history
    history = IncidentHistory(
        incident_id=incident.id,
        action="INCIDENT_CREATED",
        old_value=None,
        new_value=incident.status.value,
        changed_by=incident_in.reporter_id,
        created_at=now,
    )
    db.add(history)
    db.commit()
    db.refresh(incident)

    logger.info(
        f"Created incident {incident.incident_number}",
        extra={
            "operation": "create_incident",
            "incident_id": incident.id,
            "incident_number": incident.incident_number,
            "priority": incident.priority.value,
        }
    )
    return incident


def update_incident(db: Session, incident: Incident, update_in: IncidentUpdate) -> Incident:
    """Update general fields of an incident."""
    now = datetime.now(timezone.utc)
    update_data = update_in.model_dump(exclude_unset=True)

    for field, val in update_data.items():
        setattr(incident, field, val)

    incident.updated_at = now
    db.commit()
    db.refresh(incident)

    logger.info(
        f"Updated incident {incident.incident_number}",
        extra={"operation": "update_incident", "incident_id": incident.id}
    )
    return incident


def change_incident_status(
    db: Session,
    incident: Incident,
    new_status: IncidentStatus,
    changed_by: int | None = None
) -> Incident:
    """Change status of an incident and write to history."""
    old_status = incident.status.value
    now = datetime.now(timezone.utc)

    incident.status = new_status
    incident.updated_at = now

    if new_status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
        if not incident.resolved_at:
            incident.resolved_at = now
    else:
        incident.resolved_at = None

    history = IncidentHistory(
        incident_id=incident.id,
        action="STATUS_CHANGED",
        old_value=old_status,
        new_value=new_status.value,
        changed_by=changed_by,
        created_at=now,
    )
    db.add(history)
    db.commit()
    db.refresh(incident)

    logger.info(
        f"Changed status of {incident.incident_number} from {old_status} to {new_status.value}",
        extra={
            "operation": "change_incident_status",
            "incident_id": incident.id,
            "old_status": old_status,
            "new_status": new_status.value,
            "changed_by": changed_by,
        }
    )
    return incident


def change_incident_priority(
    db: Session,
    incident: Incident,
    new_priority: Priority,
    changed_by: int | None = None
) -> Incident:
    """Change priority of an incident and write to history."""
    old_priority = incident.priority.value
    now = datetime.now(timezone.utc)

    incident.priority = new_priority
    incident.updated_at = now

    history = IncidentHistory(
        incident_id=incident.id,
        action="PRIORITY_CHANGED",
        old_value=old_priority,
        new_value=new_priority.value,
        changed_by=changed_by,
        created_at=now,
    )
    db.add(history)
    db.commit()
    db.refresh(incident)

    logger.info(
        f"Changed priority of {incident.incident_number} from {old_priority} to {new_priority.value}",
        extra={
            "operation": "change_incident_priority",
            "incident_id": incident.id,
            "old_priority": old_priority,
            "new_priority": new_priority.value,
            "changed_by": changed_by,
        }
    )
    return incident


def assign_incident(
    db: Session,
    incident: Incident,
    assigned_to: int | None,
    changed_by: int | None = None
) -> Incident:
    """Assign an incident to a technician and write to history."""
    old_assignee_id = str(incident.assigned_to) if incident.assigned_to else "Unassigned"
    new_assignee_id = str(assigned_to) if assigned_to else "Unassigned"
    now = datetime.now(timezone.utc)

    incident.assigned_to = assigned_to
    incident.updated_at = now

    history = IncidentHistory(
        incident_id=incident.id,
        action="ASSIGNMENT_CHANGED",
        old_value=old_assignee_id,
        new_value=new_assignee_id,
        changed_by=changed_by,
        created_at=now,
    )
    db.add(history)
    db.commit()
    db.refresh(incident)

    logger.info(
        f"Assigned incident {incident.incident_number} to user {assigned_to}",
        extra={
            "operation": "assign_incident",
            "incident_id": incident.id,
            "assigned_to": assigned_to,
            "changed_by": changed_by,
        }
    )
    return incident


def add_comment(db: Session, incident_id: int, user_id: int, comment_text: str) -> Comment:
    """Add comment to an incident."""
    now = datetime.now(timezone.utc)
    comment = Comment(
        incident_id=incident_id,
        user_id=user_id,
        comment=comment_text,
        created_at=now
    )
    db.add(comment)

    # Also log history event for comment added
    history = IncidentHistory(
        incident_id=incident_id,
        action="COMMENT_ADDED",
        old_value=None,
        new_value=f"Comment by User #{user_id}",
        changed_by=user_id,
        created_at=now,
    )
    db.add(history)
    db.commit()
    db.refresh(comment)

    logger.info(
        f"Added comment to incident ID {incident_id}",
        extra={
            "operation": "add_comment",
            "incident_id": incident_id,
            "user_id": user_id,
        }
    )
    return comment


def get_incident_comments(db: Session, incident_id: int) -> list[Comment]:
    """Retrieve comments for an incident."""
    return db.query(Comment).filter(Comment.incident_id == incident_id).order_by(desc(Comment.created_at)).all()


def get_incident_history(db: Session, incident_id: int) -> list[IncidentHistory]:
    """Retrieve history timeline for an incident."""
    return db.query(IncidentHistory).filter(IncidentHistory.incident_id == incident_id).order_by(desc(IncidentHistory.created_at)).all()


def delete_incident(db: Session, incident: Incident) -> None:
    """Delete an incident."""
    inc_id = incident.id
    inc_num = incident.incident_number
    db.delete(incident)
    db.commit()
    logger.info(
        f"Deleted incident {inc_num}",
        extra={"operation": "delete_incident", "incident_id": inc_id}
    )
