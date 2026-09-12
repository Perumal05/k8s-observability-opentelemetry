import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logging_config import setup_logging, get_logger
from app.database.init_db import init_db
from app.services.background_service import process_incident_statistics
from app.api import (
    incidents_router,
    users_router,
    comments_router,
    dashboard_router,
    health_router,
)

# Initialize structured logging
setup_logging()
logger = get_logger("opsdesk.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: database initialization and background task orchestration."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] environment...")

    # Initialize Database Schema & Seed Data
    try:
        init_db()
        logger.info("Database schema initialized and ready.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

    # Start lightweight background statistics worker
    bg_task = asyncio.create_task(process_incident_statistics())

    yield

    # Graceful shutdown
    logger.info("Shutting down background workers and releasing resources...")
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass
    logger.info(f"{settings.APP_NAME} shutdown complete.")


app = FastAPI(
    title="OpsDesk API",
    description="OpsDesk IT Incident Management Platform API.",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(incidents_router)
app.include_router(users_router)
app.include_router(comments_router)
app.include_router(dashboard_router)


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Welcome to OpsDesk API",
        "documentation": "/docs",
        "health": "/health",
        "ready": "/ready"
    }
