import os
import json
import requests

CONFIG_PATH = "config/config.json"
OUTPUT_DIR = "models"


def load_config():
    with open(CONFIG_PATH, "r") as f:
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


def download_file(file_id, filename, access_token):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)

    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"Downloaded: {filepath}")


def main():
    config = load_config()

    file_id = config["model"]["base_model_drive_file_id"]
    filename = config["model"]["base_model"]

    access_token = get_access_token()

    download_file(file_id, filename, access_token)


if __name__ == "__main__":
    main()
