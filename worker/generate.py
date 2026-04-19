import os

USE_GPU = os.getenv("USE_GPU", "false") == "true"


def generate(prompt: str):
    # Placeholder for SDXL
    # In real deploy, load diffusers pipeline here
    return f"generated_image_for_{prompt}.png"
