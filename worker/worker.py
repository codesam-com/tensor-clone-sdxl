from rq import Worker
from services.queue import redis_conn

if __name__ == "__main__":
    worker = Worker(["premium", "free"], connection=redis_conn)
    worker.work()
