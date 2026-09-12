from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base


class UserRole(str, enum.Enum):
    REPORTER = "REPORTER"
    TECHNICIAN = "TECHNICIAN"
    MANAGER = "MANAGER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole, name="user_roles"), nullable=False, default=UserRole.REPORTER)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    reported_incidents = relationship("Incident", foreign_keys="Incident.reporter_id", back_populates="reporter")
    assigned_incidents = relationship("Incident", foreign_keys="Incident.assigned_to", back_populates="assignee")
    comments = relationship("Comment", back_populates="user")
