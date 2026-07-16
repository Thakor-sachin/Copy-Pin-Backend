import redis
from app.core.config import settings

# Initialize Redis client with string decoding enabled
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Helper function to get Redis instance
def get_redis():
    return redis_client
