import time
import subprocess
import sys

cmd = [
    sys.executable,
    "ComfyUI/main.py",
    "--listen",
    "127.0.0.1",
    "--port",
    "8188",
    "--cpu"
]

process = subprocess.Popen(cmd)

time.sleep(20)

if process.poll() is None:
    print("ComfyUI started successfully.")
    process.terminate()
    process.wait(timeout=10)
else:
    raise RuntimeError("ComfyUI failed to start.")
