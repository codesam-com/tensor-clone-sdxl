import os
import redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = redis.from_url(REDIS_URL)
job_queue = Queue("image-generation", connection=redis_conn)


def job_key(job_id: str) -> str:
    return f"job:{job_id}"
