from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "copypin_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Apply configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "cleanup-expired-shares-every-30-mins": {
            "task": "cleanup_expired_pins",
            "schedule": 1800.0,  # Run every 30 minutes
        },
    }
)

@celery_app.task(name="cleanup_expired_pins")
def cleanup_expired_pins():
    """
    Task to cleanup expired PIN uploads and files from database and storage.
    """
    from app.core.database import SessionLocal
    from app.services import share_service
    
    db = SessionLocal()
    try:
        deleted_count = share_service.cleanup_expired_shares_job(db)
        return f"Successfully cleaned up {deleted_count} expired shares"
    finally:
        db.close()
