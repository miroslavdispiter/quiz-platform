import json
import redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from app.config import Config

# Cache keys
PUBLISHED_QUIZZES_KEY = "quizzes:published"


def leaderboard_key(quiz_id: str) -> str:
    return f"leaderboard:{quiz_id}"


class Cache:
    """
    Redis cache for data that is read often and changes rarely.
    If Redis is not running, every method simply does nothing (get returns None),
    so the service keeps working directly with MongoDB.
    """

    def __init__(self):
        self.client = redis.Redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            retry=Retry(NoBackoff(), 0),  # no retries: if Redis is down, go to MongoDB right away
        )

    def get(self, key: str):
        """Returns the saved data, or None if it is not in the cache."""
        try:
            value = self.client.get(key)
        except redis.RedisError:
            print("[cache] Redis is not available - reading from MongoDB")
            return None

        if value is None:
            print(f"[cache] MISS {key}")
            return None

        print(f"[cache] HIT {key}")
        return json.loads(value)

    def set(self, key: str, data):
        """Saves data in the cache for CACHE_TTL_SECONDS."""
        try:
            self.client.setex(key, Config.CACHE_TTL_SECONDS, json.dumps(data))
        except redis.RedisError:
            pass

    def delete(self, *keys: str):
        """Removes data from the cache (called when the data changes)."""
        try:
            self.client.delete(*keys)
            print(f"[cache] DELETE {', '.join(keys)}")
        except redis.RedisError:
            pass


cache = Cache()
