import httpx
from typing import Any
from database import settings

_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


async def fetch_jobs(
    keywords: str = "software engineer",
    country: str = "us",
    page: int = 1,
    results_per_page: int = 50,
) -> list[dict[str, Any]]:
    url = f"{_BASE_URL}/{country}/search/{page}"
    params: dict[str, Any] = {
        "app_id": settings.ADZUNA_APP_ID,
        "app_key": settings.ADZUNA_APP_KEY,
        "what": keywords,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return [_normalize(r) for r in data.get("results", [])]


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "adzuna_id": str(raw.get("id", "")),
        "title": raw.get("title", ""),
        "company": (raw.get("company") or {}).get("display_name"),
        "location": (raw.get("location") or {}).get("display_name"),
        "description": raw.get("description", ""),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "category": (raw.get("category") or {}).get("label"),
        "url": raw.get("redirect_url", ""),
    }
