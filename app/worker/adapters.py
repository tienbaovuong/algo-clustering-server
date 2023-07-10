import httpx

from config.config import settings

backend = httpx.Client(
    base_url=settings.get("API_URL", "http://clustering:8001"),
    headers={
        "token": settings.get("INTERNAL_TOKEN", "default_token"),
        "x-purge-cache": "true",
    },
    timeout=60,
)
