"""Geocode location names to coordinates + country code using Nominatim."""

import re
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
COORD_RE = re.compile(r"^(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)$")


async def geocode(location: str) -> dict | None:
    """Convert location name or coordinates to lat/lng + country_code.

    Accepts: "Basel", "47.5596, 7.5886", "47.5596 7.5886"
    Returns: {"lat": float, "lng": float, "country_code": str, "display_name": str} or None
    """
    # Check if input is coordinates
    match = COORD_RE.match(location.strip())
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            # Reverse geocode to get country code
            country_code = "US"
            async with httpx.AsyncClient() as client:
                resp = await client.get(NOMINATIM_REVERSE_URL, params={
                    "lat": lat, "lon": lng, "format": "json", "addressdetails": 1,
                }, headers={"User-Agent": "MapSearch.app/1.0"})
                data = resp.json()
                if "address" in data:
                    country_code = data["address"].get("country_code", "us").upper()
            return {
                "lat": lat, "lng": lng,
                "country_code": country_code,
                "display_name": f"{lat}, {lng}",
            }

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
