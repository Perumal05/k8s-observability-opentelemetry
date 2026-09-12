from app.api.incidents import router as incidents_router
from app.api.users import router as users_router
from app.api.comments import router as comments_router
from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router

__all__ = [
    "incidents_router",
    "users_router",
    "comments_router",
    "dashboard_router",
    "health_router",
]
