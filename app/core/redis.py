import logging
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
except Exception as e:
    logger.warning(f"⚠️ Initial Redis client setup warning: {e}")
    redis_client = None


def get_redis():
    if redis_client is not None:
        try:
            redis_client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
    return redis_client