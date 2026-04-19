import os
import requests
import time
from services.s3_storage import upload_base64_image
from services.queue import redis_conn, job_key
from services.runpod_pool import pool

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
MAX_RETRIES = int(os.getenv("RUNPOD_MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("RUNPOD_TIMEOUT", "120"))


def process_job(job_id: str, prompt: str):
    redis_conn.hset(job_key(job_id), mapping={"status": "processing"})

    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(MAX_RETRIES):
        try:
            endpoint = pool.next_endpoint()

            payload = {"input": {"prompt": prompt}}

            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            runpod_id = response.json().get("id")

            status_url = f"{endpoint}/{runpod_id}"

            start = time.time()

            while time.time() - start < TIMEOUT:
                r = requests.get(status_url, headers=headers, timeout=10).json()

                if r.get("status") == "COMPLETED":
                    base64_img = r.get("output", {}).get("image_base64")
                    url = upload_base64_image(base64_img)

                    redis_conn.hset(job_key(job_id), mapping={
                        "status": "completed",
                        "image_url": url
                    })
                    return

                if r.get("status") == "FAILED":
                    raise Exception("RunPod job failed")

                time.sleep(2)

            raise TimeoutError("RunPod timeout")

        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                redis_conn.hset(job_key(job_id), mapping={
                    "status": "failed",
                    "error": str(e)
                })
                return

            time.sleep(2 * (attempt + 1))
