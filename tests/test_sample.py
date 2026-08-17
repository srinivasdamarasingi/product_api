import redis
import os

def test_redis_connection():
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=6379,
        decode_responses=True
    )

    client.set("name", "Srinivas")

    assert client.get("name") == "Srinivas"