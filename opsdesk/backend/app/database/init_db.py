import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.incident import Incident, IncidentHistory, Priority, IncidentStatus, IncidentCategory
from app.models.comment import Comment
from app.database.connection import engine, SessionLocal

logger = logging.getLogger(__name__)


def init_db():
    """Create database tables and seed initial data if empty."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as db:
        seed_data(db)


def seed_data(db: Session):
    """Seed users, sample incidents, comments, and history if database is empty."""
    user_count = db.query(User).count()
    if user_count > 0:
        logger.info("Database already contains user records. Skipping seed.")
        return

    logger.info("Seeding initial users and incidents...")
    now = datetime.now(timezone.utc)

    # 1. Seed Users
    users = [
        User(name="Alice Tech", email="alice.tech@opsdesk.io", role=UserRole.TECHNICIAN, created_at=now - timedelta(days=30)),
        User(name="Bob Network", email="bob.network@opsdesk.io", role=UserRole.TECHNICIAN, created_at=now - timedelta(days=30)),
        User(name="Carol DBA", email="carol.dba@opsdesk.io", role=UserRole.TECHNICIAN, created_at=now - timedelta(days=30)),
        User(name="David DevOps", email="david.devops@opsdesk.io", role=UserRole.TECHNICIAN, created_at=now - timedelta(days=30)),
        User(name="Sarah Connor", email="sarah.reporter@opsdesk.io", role=UserRole.REPORTER, created_at=now - timedelta(days=30)),
        User(name="John Doe", email="john.reporter@opsdesk.io", role=UserRole.REPORTER, created_at=now - timedelta(days=30)),
        User(name="Elena Rostova", email="elena.manager@opsdesk.io", role=UserRole.MANAGER, created_at=now - timedelta(days=30)),
    ]
    db.add_all(users)
    db.commit()

    # Re-fetch users for IDs
    tech_alice = db.query(User).filter_by(email="alice.tech@opsdesk.io").first()
    tech_bob = db.query(User).filter_by(email="bob.network@opsdesk.io").first()
    tech_carol = db.query(User).filter_by(email="carol.dba@opsdesk.io").first()
    tech_david = db.query(User).filter_by(email="david.devops@opsdesk.io").first()
    rep_sarah = db.query(User).filter_by(email="sarah.reporter@opsdesk.io").first()
    rep_john = db.query(User).filter_by(email="john.reporter@opsdesk.io").first()

    # 2. Seed Realistic Incidents
    sample_incidents = [
        {
            "incident_number": "INC-1001",
            "title": "Payment Gateway API Latency Spike (>3500ms)",
            "description": "Payment microservice checkout requests are timing out for US-East region users. Error rate increased to 12%.",
            "priority": Priority.CRITICAL,
            "status": IncidentStatus.IN_PROGRESS,
            "category": IncidentCategory.APPLICATION,
            "reporter_id": rep_sarah.id,
            "assigned_to": tech_alice.id,
            "created_at": now - timedelta(hours=2),
            "updated_at": now - timedelta(minutes=25),
            "resolved_at": None,
            "comments": [
                (tech_alice.id, "Investigating upstream third-party gateway response times.", now - timedelta(hours=1, minutes=30)),
                (tech_alice.id, "Identified connection pool exhaustion on redis cache layer.", now - timedelta(minutes=25)),
            ],
            "history": [
                ("INCIDENT_CREATED", None, "OPEN", rep_sarah.id, now - timedelta(hours=2)),
                ("STATUS_CHANGED", "OPEN", "IN_PROGRESS", tech_alice.id, now - timedelta(hours=1, minutes=45)),
                ("PRIORITY_CHANGED", "HIGH", "CRITICAL", tech_alice.id, now - timedelta(hours=1, minutes=35)),
            ]
        },
        {
            "incident_number": "INC-1002",
            "title": "Core Router BGP Flapping in Zone 2",
            "description": "Border Gateway Protocol session flapping on router cr02.sfo. Periodic packet drop of 4% observed.",
            "priority": Priority.HIGH,
            "status": IncidentStatus.OPEN,
            "category": IncidentCategory.NETWORK,
            "reporter_id": rep_john.id,
            "assigned_to": tech_bob.id,
            "created_at": now - timedelta(hours=4),
            "updated_at": now - timedelta(hours=4),
            "resolved_at": None,
            "comments": [
                (rep_john.id, "Automated alert triggered from Prometheus network probe.", now - timedelta(hours=3, minutes=50))
            ],
            "history": [
                ("INCIDENT_CREATED", None, "OPEN", rep_john.id, now - timedelta(hours=4)),
            ]
        },
        {
            "incident_number": "INC-1003",
            "title": "PostgreSQL Main Replica Replication Lag > 450s",
            "description": "Read-replica replica-02 in cluster postgres-prod is lagging behind primary due to heavy batch analytical query.",
            "priority": Priority.HIGH,
            "status": IncidentStatus.RESOLVED,
            "category": IncidentCategory.DATABASE,
            "reporter_id": rep_sarah.id,
            "assigned_to": tech_carol.id,
            "created_at": now - timedelta(days=1, hours=3),
            "updated_at": now - timedelta(days=1, hours=1),
            "resolved_at": now - timedelta(days=1, hours=1),
            "comments": [
                (tech_carol.id, "Terminated blocking query PID 49201. Replication recovered.", now - timedelta(days=1, hours=1))
            ],
            "history": [
                ("INCIDENT_CREATED", None, "OPEN", rep_sarah.id, now - timedelta(days=1, hours=3)),
                ("STATUS_CHANGED", "OPEN", "IN_PROGRESS", tech_carol.id, now - timedelta(days=1, hours=2)),
                ("STATUS_CHANGED", "IN_PROGRESS", "RESOLVED", tech_carol.id, now - timedelta(days=1, hours=1)),
            ]
        },
        {
            "incident_number": "INC-1004",
            "title": "SSL Certificate Expiry Warning for internal auth proxy",
            "description": "auth-proxy.internal.corp certificate expires in 72 hours. Automated certbot renew failed.",
            "priority": Priority.MEDIUM,
            "status": IncidentStatus.PENDING,
            "category": IncidentCategory.SECURITY,
            "reporter_id": rep_john.id,
            "assigned_to": tech_david.id,
            "created_at": now - timedelta(hours=6),
            "updated_at": now - timedelta(hours=1),
            "resolved_at": None,
            "comments": [
                (tech_david.id, "Pending DNS challenge authorization token from infosec team.", now - timedelta(hours=1))
            ],
            "history": [
                ("INCIDENT_CREATED", None, "OPEN", rep_john.id, now - timedelta(hours=6)),
                ("STATUS_CHANGED", "OPEN", "PENDING", tech_david.id, now - timedelta(hours=1)),
            ]
        },
        {
            "incident_number": "INC-1005",
            "title": "Kubelet Memory Pressure on worker-node-04",
            "description": "Node worker-04 triggered MemoryPressure taint. Non-critical batch pods being evicted.",
            "priority": Priority.LOW,
            "status": IncidentStatus.CLOSED,
            "category": IncidentCategory.HARDWARE,
            "reporter_id": rep_sarah.id,
            "assigned_to": tech_david.id,
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(days=1, hours=18),
            "resolved_at": now - timedelta(days=1, hours=20),
            "comments": [
                (tech_david.id, "Cleaned up orphaned docker overlay filesystem layers.", now - timedelta(days=1, hours=20))
            ],
            "history": [
                ("INCIDENT_CREATED", None, "OPEN", rep_sarah.id, now - timedelta(days=2)),
                ("STATUS_CHANGED", "OPEN", "RESOLVED", tech_david.id, now - timedelta(days=1, hours=20)),
                ("STATUS_CHANGED", "RESOLVED", "CLOSED", tech_david.id, now - timedelta(days=1, hours=18)),
            ]
        },
    ]

    for item in sample_incidents:
        inc = Incident(
            incident_number=item["incident_number"],
            title=item["title"],
            description=item["description"],
            priority=item["priority"],
            status=item["status"],
            category=item["category"],
            reporter_id=item["reporter_id"],
            assigned_to=item["assigned_to"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            resolved_at=item["resolved_at"]
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)

        # Add comments
        for user_id, comm_text, comm_time in item["comments"]:
            c = Comment(incident_id=inc.id, user_id=user_id, comment=comm_text, created_at=comm_time)
            db.add(c)

        # Add history
        for action, old_v, new_v, ch_by, ch_time in item["history"]:
            h = IncidentHistory(
                incident_id=inc.id,
                action=action,
                old_value=old_v,
                new_value=new_v,
                changed_by=ch_by,
                created_at=ch_time
            )
            db.add(h)

        db.commit()

    logger.info("Sample seed data created successfully.")
