import logging
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis import get_redis

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", summary="System Health Check")
def health_check(
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis)
):
    db_status = "unhealthy"
    redis_status = "unhealthy"

    # Test database connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = str(e)

    # Test Redis connection
    try:
        redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        redis_status = str(e)

    # Overall status
    status = "healthy"
    if db_status != "healthy" or redis_status != "healthy":
        status = "degraded"

    return {
        "status": status,
        "services": {
            "database": db_status,
            "redis": redis_status
        }
    }