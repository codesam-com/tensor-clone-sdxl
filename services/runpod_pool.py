import os
from itertools import cycle
from threading import Lock


def _parse_endpoints() -> list[str]:
    raw = os.getenv("RUNPOD_ENDPOINTS", "")
    endpoints = [item.strip() for item in raw.split(",") if item.strip()]
    if endpoints:
        return endpoints

    fallback = os.getenv("RUNPOD_ENDPOINT", "").strip()
    return [fallback] if fallback else []


class RunpodEndpointPool:
    def __init__(self) -> None:
        self._lock = Lock()
        self._endpoints = _parse_endpoints()
        self._iterator = cycle(self._endpoints) if self._endpoints else None

    def next_endpoint(self) -> str:
        if not self._iterator:
            raise RuntimeError("No RunPod endpoints configured")
        with self._lock:
            return next(self._iterator)


pool = RunpodEndpointPool()
