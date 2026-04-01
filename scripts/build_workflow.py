import json
import os
import random

CONFIG_PATH = "config/config.json"
TEMPLATE_PATH = "comfy/workflow.json"
OUTPUT_PATH = "comfy/workflow.runtime.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_enabled_loras(config):
    return [lora for lora in config.get("loras", []) if lora.get("enabled", False)]


def main():
    config = load_json(CONFIG_PATH)
    workflow = load_json(TEMPLATE_PATH)

    job = config["jobs"][0]
    generation = config["generation"]
    model = config["model"]
    enabled_loras = get_enabled_loras(config)

    seed = job["seed"]
    if seed is None:
        seed = random.randint(1, 2**31 - 1)

    workflow["4"]["inputs"]["ckpt_name"] = model["base_model"]
    workflow["5"]["inputs"]["width"] = generation["width"]
    workflow["5"]["inputs"]["height"] = generation["height"]
    workflow["6"]["inputs"]["text"] = job["prompt"]
    workflow["7"]["inputs"]["text"] = job["negative_prompt"]
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["steps"] = generation["steps"]
    workflow["3"]["inputs"]["cfg"] = generation["cfg"]
    workflow["3"]["inputs"]["sampler_name"] = generation["sampler"]
    workflow["3"]["inputs"]["scheduler"] = generation["scheduler"]

    workflow["9"]["inputs"]["filename_prefix"] = f"{seed}_base"
    workflow["12"]["inputs"]["filename_prefix"] = f"{seed}_upscaled"

    first_lora = enabled_loras[0] if len(enabled_loras) > 0 else None
    second_lora = enabled_loras[1] if len(enabled_loras) > 1 else None

    if first_lora:
        workflow["13"]["inputs"]["lora_name"] = first_lora["name"]
        workflow["13"]["inputs"]["strength_model"] = first_lora["strength"]
        workflow["13"]["inputs"]["strength_clip"] = first_lora["strength"]
    else:
        workflow["13"]["inputs"]["lora_name"] = "add_more_details_xl.safetensors"
        workflow["13"]["inputs"]["strength_model"] = 0
        workflow["13"]["inputs"]["strength_clip"] = 0

    if second_lora:
        workflow["14"]["inputs"]["lora_name"] = second_lora["name"]
        workflow["14"]["inputs"]["strength_model"] = second_lora["strength"]
        workflow["14"]["inputs"]["strength_clip"] = second_lora["strength"]
    else:
        workflow["14"]["inputs"]["lora_name"] = "age_slider_ponyxl.safetensors"
        workflow["14"]["inputs"]["strength_model"] = 0
        workflow["14"]["inputs"]["strength_clip"] = 0

    os.makedirs("comfy", exist_ok=True)
    save_json(OUTPUT_PATH, workflow)

    print(f"Workflow built: {OUTPUT_PATH}")
    print(f"Seed used: {seed}")
    print(f"Enabled LoRAs: {[l['name'] for l in enabled_loras]}")


if __name__ == "__main__":
    main()
