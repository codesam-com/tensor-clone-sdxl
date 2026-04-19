import time
from services.queue import redis_conn


def check_rate_limit(user):
    key = f"rate:{user.id}"
    current = redis_conn.get(key)

    if current and int(current) >= user.rate_limit_per_minute:
        raise Exception("Rate limit exceeded")

    pipe = redis_conn.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, 60)
    pipe.execute()
