import os
import requests
from services.s3_storage import upload_base64_image
from services.queue import redis_conn, job_key

RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")


def process_job(job_id: str, prompt: str):
    redis_conn.hset(job_key(job_id), mapping={"status": "processing"})

    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"input": {"prompt": prompt}}

    response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers)
    runpod_id = response.json().get("id")

    status_url = f"{RUNPOD_ENDPOINT}/{runpod_id}"

    while True:
        r = requests.get(status_url, headers=headers).json()

        if r.get("status") == "COMPLETED":
            base64_img = r.get("output", {}).get("image_base64")
            url = upload_base64_image(base64_img)

            redis_conn.hset(job_key(job_id), mapping={
                "status": "completed",
                "image_url": url
            })
            break
