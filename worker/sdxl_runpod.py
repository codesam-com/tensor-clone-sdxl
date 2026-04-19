import runpod
from diffusers import StableDiffusionXLPipeline
import torch
import base64
from io import BytesIO

pipe = None


def load_model():
    global pipe
    if pipe is None:
        pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16
        ).to("cuda")


def handler(job):
    load_model()
    prompt = job["input"]["prompt"]

    image = pipe(prompt).images[0]

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return {"image_base64": img_str}


runpod.serverless.start({"handler": handler})
