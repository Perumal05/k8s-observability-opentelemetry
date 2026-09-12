from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import incident_service

router = APIRouter(prefix="/api/incidents/{incident_id}/comments", tags=["Comments"])


@router.get("", response_model=list[CommentResponse])
def get_comments(incident_id: int, db: Session = Depends(get_db)):
    """Get all comments for a specific incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    comments = incident_service.get_incident_comments(db, incident_id=incident_id)
    return [CommentResponse.model_validate(c) for c in comments]


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def post_comment(incident_id: int, comment_in: CommentCreate, db: Session = Depends(get_db)):
    """Add a new comment to an incident."""
    incident = incident_service.get_incident_by_id(db, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")
    comment = incident_service.add_comment(
        db,
        incident_id=incident_id,
        user_id=comment_in.user_id,
        comment_text=comment_in.comment,
    )
    return CommentResponse.model_validate(comment)
