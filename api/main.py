from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uuid
from services.auth import get_api_key, deduct_credit
from api.auth_routes import router as auth_router
from api.billing_routes import router as billing_router
from services.queue import job_queue, redis_conn, job_key
from worker.jobs import process_job

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(billing_router, prefix="/billing")

class JobRequest(BaseModel):
    prompt: str

@app.post("/v1/jobs")
def create_job(req: JobRequest, api_key = Depends(get_api_key)):
    deduct_credit(api_key)

    job_id = str(uuid.uuid4())

    redis_conn.hset(job_key(job_id), mapping={"status": "queued"})

    job_queue.enqueue(process_job, job_id, req.prompt)

    return {"job_id": job_id}

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str, api_key = Depends(get_api_key)):
    data = redis_conn.hgetall(job_key(job_id))

    if not data:
        return {"error": "not found"}

    decoded = {k.decode(): v.decode() for k, v in data.items()}

    return decoded
