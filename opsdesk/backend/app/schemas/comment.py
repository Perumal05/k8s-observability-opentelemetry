from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    comment: str


class CommentCreate(CommentBase):
    user_id: int


class CommentResponse(CommentBase):
    id: int
    incident_id: int
    user_id: int
    created_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
