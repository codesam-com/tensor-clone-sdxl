from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import os
import requests
from services.s3_storage import upload_base64_image

app = FastAPI()

jobs = {}

RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")

class JobRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/jobs")
def create_job(req: JobRequest):
    job_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": req.prompt
        }
    }

    response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers)
    data = response.json()

    jobs[job_id] = {
        "status": "submitted",
        "runpod_id": data.get("id"),
        "prompt": req.prompt
    }

    return {"job_id": job_id}

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"error": "not found"}

    runpod_id = job.get("runpod_id")

    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }

    status_url = f"{RUNPOD_ENDPOINT}/{runpod_id}"
    response = requests.get(status_url, headers=headers)
    data = response.json()

    if data.get("status") == "COMPLETED":
        base64_img = data.get("output", {}).get("image_base64")
        if base64_img:
            url = upload_base64_image(base64_img)
            return {
                "status": "COMPLETED",
                "image_url": url
            }

    return {
        "status": data.get("status")
    }
