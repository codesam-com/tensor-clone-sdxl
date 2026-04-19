from rq import Worker
from services.queue import redis_conn

if __name__ == "__main__":
    worker = Worker(["image-generation"], connection=redis_conn)
    worker.work()
