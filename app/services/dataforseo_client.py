"""Async DataForSEO Google Maps Live API client."""

import httpx
from app.config import DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, DATAFORSEO_MAX_DEPTH

LIVE_ENDPOINT = "https://api.dataforseo.com/v3/serp/google/maps/live/advanced"


async def search_maps(keyword, lat, lng, zoom, location_code, language_code, near_me=False):
    """Search Google Maps via DataForSEO live/sync API. Returns results in seconds."""
    payload = [{
        "keyword": f"{keyword} near me" if near_me else keyword,
        "location_coordinate": f"{lat},{lng},{zoom}",
        "location_code": location_code,
        "language_code": language_code,
        "depth": DATAFORSEO_MAX_DEPTH,
        "device": "desktop",
    }]
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            LIVE_ENDPOINT, json=payload,
            auth=(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD),
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()
