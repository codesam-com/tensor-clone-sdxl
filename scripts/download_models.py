import os
import json
import requests

CONFIG_PATH = "config/config.json"
OUTPUT_DIR = "models"
LORA_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "loras")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_access_token():
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": os.environ["GDRIVE_CLIENT_ID"],
        "client_secret": os.environ["GDRIVE_CLIENT_SECRET"],
        "refresh_token": os.environ["GDRIVE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def download_file(file_id, filepath, access_token):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"Downloaded: {filepath}")


def main():
    config = load_config()
    access_token = get_access_token()

    base_model_name = config["model"]["base_model"]
    base_model_file_id = config["model"]["base_model_drive_file_id"]
    base_model_path = os.path.join(OUTPUT_DIR, base_model_name)

    download_file(base_model_file_id, base_model_path, access_token)

    for lora in config.get("loras", []):
        lora_name = lora["name"]
        lora_file_id = lora["drive_file_id"]
        lora_path = os.path.join(LORA_OUTPUT_DIR, lora_name)

        download_file(lora_file_id, lora_path, access_token)


if __name__ == "__main__":
    main()
