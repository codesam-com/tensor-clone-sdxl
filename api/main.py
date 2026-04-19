from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

jobs = {}

class JobRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/jobs")
def create_job(req: JobRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "prompt": req.prompt}
    return {"job_id": job_id}

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "not found"})
