import json
import os
import time
import requests

CONFIG_PATH = "config/config.json"
OUTPUT_DIR = "models"
LORA_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "loras")

TOKEN_URL = "https://oauth2.googleapis.com/token"
DRIVE_FILE_URL = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

DOWNLOAD_TIMEOUT = 120
CHUNK_SIZE = 1024 * 1024  # 1 MB
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 5


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_access_token():
    data = {
        "client_id": os.environ["GDRIVE_CLIENT_ID"],
        "client_secret": os.environ["GDRIVE_CLIENT_SECRET"],
        "refresh_token": os.environ["GDRIVE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }

    response = requests.post(TOKEN_URL, data=data, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


def download_file(file_id, filepath, access_token):
    url = DRIVE_FILE_URL.format(file_id=file_id)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)

            print(f"Downloading to {filepath} (attempt {attempt}/{MAX_RETRIES})")

            with requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=DOWNLOAD_TIMEOUT,
            ) as response:
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)

            file_size = os.path.getsize(filepath)
            if file_size <= 0:
                raise RuntimeError(f"Downloaded file is empty: {filepath}")

            print(f"Downloaded successfully: {filepath} ({file_size} bytes)")
            return

        except Exception as e:
            print(f"Download failed for {filepath}: {e}")

            if os.path.exists(filepath):
                os.remove(filepath)

            if attempt == MAX_RETRIES:
                raise

            print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)


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
