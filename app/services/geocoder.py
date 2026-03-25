"""Geocode location names to coordinates + country code using Nominatim."""

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


async def geocode(location: str) -> dict | None:
    """Convert location name to lat/lng + country_code.

    Returns: {"lat": float, "lng": float, "country_code": str, "display_name": str} or None
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(NOMINATIM_URL, params={
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }, headers={"User-Agent": "MapSearch.app/1.0"})
        results = resp.json()
        if not results:
            return None
        r = results[0]
        return {
            "lat": float(r["lat"]),
            "lng": float(r["lon"]),
            "country_code": r.get("address", {}).get("country_code", "us").upper(),
            "display_name": r["display_name"],
        }
