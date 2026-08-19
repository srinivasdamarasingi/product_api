import time

from app.services.redis_service import redis_client


def is_rate_limited(
    key: str,
    limit: int = 5,
    window_seconds: int = 60
) -> bool:

    current_window = int(time.time() // window_seconds)

    redis_key = f"rate_limit:{key}:{current_window}"

    request_count = redis_client.incr(redis_key)

    if request_count == 1:
        redis_client.expire(
            redis_key,
            window_seconds
        )

    return request_count > limit