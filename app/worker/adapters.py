import httpx

from config.config import settings

backend = httpx.Client(
    base_url=settings.get("API_URL", "http://localhost:8001"),
    headers={
        "x-purge-cache": "true",
    },
    timeout=60,
)
