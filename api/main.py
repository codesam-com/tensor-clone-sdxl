from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uuid
from services.auth import get_api_key, deduct_credit
from api.auth_routes import router as auth_router
from api.billing_routes import router as billing_router
from services.queue import get_queue, redis_conn, job_key
from services.rate_limit import check_rate_limit
from worker.jobs import process_job

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(billing_router, prefix="/billing")

class JobRequest(BaseModel):
    prompt: str

@app.post("/v1/jobs")
def create_job(req: JobRequest, user = Depends(get_api_key)):
    check_rate_limit(user)
    deduct_credit(user)

    job_id = str(uuid.uuid4())

    redis_conn.hset(job_key(job_id), mapping={"status": "queued"})

    queue = get_queue(user)
    queue.enqueue(process_job, job_id, req.prompt)

    return {"job_id": job_id}

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str, user = Depends(get_api_key)):
    data = redis_conn.hgetall(job_key(job_id))

    if not data:
        return {"error": "not found"}

    decoded = {k.decode(): v.decode() for k, v in data.items()}

    return decoded
