import json
import os
import shutil

CONFIG_PATH = "config/config.json"
DOWNLOADED_MODELS_DIR = "models"
COMFY_CHECKPOINTS_DIR = "ComfyUI/models/checkpoints"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config()
    base_model = config["model"]["base_model"]

    src = os.path.join(DOWNLOADED_MODELS_DIR, base_model)
    dst_dir = COMFY_CHECKPOINTS_DIR
    dst = os.path.join(dst_dir, base_model)

    if not os.path.exists(src):
        raise FileNotFoundError(f"Base model not found: {src}")

    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src, dst)

    print(f"Copied model to: {dst}")


if __name__ == "__main__":
    main()
