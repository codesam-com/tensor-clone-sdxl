import os
from fastapi import Header, HTTPException

API_KEYS = {
    os.getenv("DEFAULT_API_KEY", "test-key"): {
        "credits": 100
    }
}


def get_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def deduct_credit(api_key: str):
    if API_KEYS[api_key]["credits"] <= 0:
        raise HTTPException(status_code=402, detail="No credits left")
    API_KEYS[api_key]["credits"] -= 1
