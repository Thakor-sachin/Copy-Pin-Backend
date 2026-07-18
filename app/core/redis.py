import logging
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )

    # Test Redis connection immediately
    redis_client.ping()
    logger.info("✅ Redis connected successfully")

except Exception as e:
    logger.exception("❌ Redis connection failed")
    raise


def get_redis():
    return redis_client