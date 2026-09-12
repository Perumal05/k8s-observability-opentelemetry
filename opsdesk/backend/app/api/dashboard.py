from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.dashboard import DashboardSummary, DashboardStatistics
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve high-level incident summary metrics for dashboard KPIs."""
    return dashboard_service.calculate_dashboard_summary(db=db)


@router.get("/statistics", response_model=DashboardStatistics)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """Retrieve detailed incident distribution by priority, status, and category."""
    return dashboard_service.calculate_dashboard_statistics(db=db)
