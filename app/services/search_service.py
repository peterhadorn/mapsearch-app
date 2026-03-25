"""Search orchestration — cache check, geocode, API call, filter, credit deduction."""

import json

from app.services.geocoder import geocode
from app.services.location_resolver import resolve_location
from app.services import dataforseo_client
from app.services.credit_service import deduct_credits, get_balance
from app.database.connection import fetchrow, fetch, execute
from app.config import CACHE_DURATION_HOURS, DATAFORSEO_MAX_DEPTH


class InsufficientCreditsError(Exception):
    def __init__(self, needed, available):
        self.needed = needed
        self.available = available


async def find_cached_scrape(cache_key, max_age_hours=72):
    """Find a cached raw scrape within the max age window."""
    return await fetchrow("""
        SELECT id, raw_result_count FROM scrape_cache
        WHERE cache_key = $1
        AND created_at > NOW() - make_interval(hours := $2)
        ORDER BY created_at DESC LIMIT 1
    """, cache_key, max_age_hours)


async def get_cached_results(scrape_cache_id):
    """Load raw results for a cached scrape."""
    return await fetch(
        "SELECT * FROM search_results WHERE scrape_cache_id = $1",
        scrape_cache_id
    )


async def store_scrape(keyword, location, lat, lng, zoom, near_me, country, results):
    """Store raw scrape results in cache."""
    cache_row = await fetchrow("""
        INSERT INTO scrape_cache (keyword, location, latitude, longitude, zoom_level, near_me, country, raw_result_count)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id
    """, keyword, location, lat, lng, zoom, near_me, country, len(results))

    scrape_cache_id = cache_row["id"]

    for r in results:
        await execute("""
            INSERT INTO search_results (
                scrape_cache_id, business_name, domain, url, phone, email, address,
                city, state, zip, country, rating, reviews_count, place_id, cid,
                google_maps_url, category, additional_categories, category_ids,
                is_claimed, verified, photos_count, main_image, latitude, longitude,
                price_level, work_hours, business_status, rating_distribution
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15,
                $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29
            )
        """, scrape_cache_id,
            r.get("title"), r.get("domain"), r.get("url"), r.get("phone"),
            r.get("email"), r.get("address"), r.get("city"), r.get("state"),
            r.get("zip"), r.get("country_code"), r.get("rating", {}).get("value"),
            r.get("rating", {}).get("votes_count"), r.get("place_id"), r.get("cid"),
            r.get("url"), r.get("category"),
            json.dumps(r.get("additional_categories", [])),
            json.dumps(r.get("category_ids", [])),
            r.get("is_claimed"), r.get("is_verified"),
            r.get("photos_count"), r.get("main_image"),
            r.get("latitude"), r.get("longitude"),
            r.get("price_level"), json.dumps(r.get("work_hours", {})),
            r.get("business_status"), json.dumps(r.get("rating_distribution", {}))
        )

    return scrape_cache_id


def apply_filters(results, filters):
    """Apply user filters to raw results. Returns filtered list."""
    filtered = list(results)

    # Tri-toggle filters: "yes", "no", "any"
    for field, db_col in [("has_website", "has_website"), ("has_email", "has_email"), ("has_phone", "has_phone")]:
        val = filters.get(field, "any")
        if val == "yes":
            filtered = [r for r in filtered if r.get(db_col)]
        elif val == "no":
            filtered = [r for r in filtered if not r.get(db_col)]

    if filters.get("is_claimed") == "yes":
        filtered = [r for r in filtered if r.get("is_claimed")]
    elif filters.get("is_claimed") == "no":
        filtered = [r for r in filtered if not r.get("is_claimed")]

    if filters.get("has_photos") == "yes":
        filtered = [r for r in filtered if (r.get("photos_count") or 0) > 0]
    elif filters.get("has_photos") == "no":
        filtered = [r for r in filtered if (r.get("photos_count") or 0) == 0]

    # Range filters
    min_rating = filters.get("min_rating", 0)
    if min_rating and min_rating > 0:
        filtered = [r for r in filtered if (r.get("rating") or 0) >= min_rating]

    min_reviews = filters.get("min_reviews", 0)
    if min_reviews and min_reviews > 0:
        filtered = [r for r in filtered if (r.get("reviews_count") or 0) >= min_reviews]

    # Category filter
    category = filters.get("category")
    if category:
        filtered = [r for r in filtered if r.get("category") == category]

    return filtered


def build_cache_key(keyword, location, zoom, near_me, country=""):
    """Build cache key matching the DB generated column formula."""
    return f"{keyword.strip().lower()}|{location.strip().lower()}|{zoom}|{str(near_me).lower()}|{(country or '').lower()}"


async def search(user_id, keyword, location, zoom_level=13, near_me=False, filters=None):
    """Main search function. Returns results dict or raises InsufficientCreditsError."""
    filters = filters or {}

    # 1. Geocode
    geo = await geocode(location)
    if not geo:
        raise ValueError(f"Could not geocode location: {location}")

    lat, lng = geo["lat"], geo["lng"]
    country_code = geo["country_code"]

    # 2. Resolve DataForSEO location
    loc_info = resolve_location(country_code)

    # 3. Check cache
    cache_key = build_cache_key(keyword, location, zoom_level, near_me, country_code)
    cached = await find_cached_scrape(cache_key, CACHE_DURATION_HOURS)

    if cached:
        scrape_cache_id = cached["id"]
        raw_results = await get_cached_results(scrape_cache_id)
        raw_results = [dict(r) for r in raw_results]
    else:
        # 4. Call DataForSEO
        api_response = await dataforseo_client.search_maps(
            keyword, lat, lng, zoom_level,
            loc_info["location_code"], loc_info["language_code"], near_me
        )

        # Parse results from DataForSEO response
        items = []
        for task in api_response.get("tasks", []):
            for result in task.get("result", []):
                items.extend(result.get("items", []))

        # Store in cache
        scrape_cache_id = await store_scrape(
            keyword, location, lat, lng, zoom_level, near_me, country_code, items
        )
        raw_results = await get_cached_results(scrape_cache_id)
        raw_results = [dict(r) for r in raw_results]

    # 5. Apply filters
    filtered_results = apply_filters(raw_results, filters)
    filtered_count = len(filtered_results)

    # 6. Credit check
    balance = await get_balance(user_id)
    if balance < filtered_count:
        raise InsufficientCreditsError(needed=filtered_count, available=balance)

    # 7. Deduct credits
    new_balance = await deduct_credits(user_id, filtered_count, reference_id=scrape_cache_id)

    # 8. Create search record
    search_row = await fetchrow("""
        INSERT INTO searches (user_id, scrape_cache_id, filters_applied, filtered_result_count, credits_used)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """, user_id, scrape_cache_id, json.dumps(filters), filtered_count, filtered_count)

    return {
        "search_id": str(search_row["id"]),
        "result_count": filtered_count,
        "credits_used": filtered_count,
        "credits_remaining": new_balance,
        "max_reached": len(raw_results) >= DATAFORSEO_MAX_DEPTH,
        "results": filtered_results,
    }
