import os
import redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = redis.from_url(REDIS_URL)

free_queue = Queue("free", connection=redis_conn)
premium_queue = Queue("premium", connection=redis_conn)


def get_queue(user):
    if user.tier in ["pro", "enterprise"]:
        return premium_queue
    return free_queue


def job_key(job_id: str) -> str:
    return f"job:{job_id}"
