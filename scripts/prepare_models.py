import json
import os
import shutil

CONFIG_PATH = "config/config.json"

DOWNLOADED_MODELS_DIR = "models"
REPO_LORAS_DIR = "assets/loras"
REPO_UPSCALE_DIR = "assets/upscale"

COMFY_CHECKPOINTS_DIR = "ComfyUI/models/checkpoints"
COMFY_LORAS_DIR = "ComfyUI/models/loras"
COMFY_UPSCALE_DIR = "ComfyUI/models/upscale_models"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def copy_file(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(f"File not found: {src}")

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Copied: {src} -> {dst}")


def main():
    config = load_config()

    base_model = config["model"]["base_model"]
    base_src = os.path.join(DOWNLOADED_MODELS_DIR, base_model)
    base_dst = os.path.join(COMFY_CHECKPOINTS_DIR, base_model)
    copy_file(base_src, base_dst)

    for lora in config.get("loras", []):
        lora_name = lora["name"]
        lora_src = os.path.join(REPO_LORAS_DIR, lora_name)
        lora_dst = os.path.join(COMFY_LORAS_DIR, lora_name)
        copy_file(lora_src, lora_dst)

    upscale = config.get("upscale", {})
    upscale_model = upscale.get("model")
    if upscale_model:
        upscale_src = os.path.join(REPO_UPSCALE_DIR, upscale_model)
        upscale_dst = os.path.join(COMFY_UPSCALE_DIR, upscale_model)
        copy_file(upscale_src, upscale_dst)


if __name__ == "__main__":
    main()
