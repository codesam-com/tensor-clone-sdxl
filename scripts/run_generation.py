import json
import os
import subprocess
import sys
import time
from urllib import request

WORKFLOW_PATH = "comfy/workflow.runtime.json"
COMFY_DIR = "ComfyUI"
OUTPUT_DIR = os.path.join(COMFY_DIR, "output")
GENERATION_TIMEOUT = 1800


def wait_for_server(url, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(2)
    return False


def main():
    cmd = [
        sys.executable,
        os.path.join(COMFY_DIR, "main.py"),
        "--listen",
        "127.0.0.1",
        "--port",
        "8188",
        "--cpu"
    ]

    process = subprocess.Popen(cmd)

    try:
        if not wait_for_server("http://127.0.0.1:8188/history"):
            raise RuntimeError("ComfyUI did not start in time.")

        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            prompt_data = json.load(f)

        payload = json.dumps({"prompt": prompt_data}).encode("utf-8")

        req = request.Request(
            "http://127.0.0.1:8188/prompt",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        prompt_id = result["prompt_id"]
        print(f"Prompt queued: {prompt_id}")

        start = time.time()
        while time.time() - start < GENERATION_TIMEOUT:
            with request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=10) as resp:
                history = json.loads(resp.read().decode("utf-8"))

            if prompt_id in history:
                print("Generation finished.")
                break

            time.sleep(3)
        else:
            raise RuntimeError("Generation timed out.")

        if not os.path.isdir(OUTPUT_DIR):
            raise RuntimeError("ComfyUI output directory not found.")

        files = os.listdir(OUTPUT_DIR)
        pngs = [f for f in files if f.lower().endswith(".png")]

        if not pngs:
            raise RuntimeError("No PNG generated.")

        print("Generated files:")
        for name in pngs:
            print(name)

    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except Exception:
            process.kill()


if __name__ == "__main__":
    main()
