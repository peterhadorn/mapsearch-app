"""Tests for search_service — all external deps mocked."""

import json
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

# Load fixture before tests
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "dataforseo_response.json"
with open(FIXTURE_PATH) as f:
    DATAFORSEO_RESPONSE = json.load(f)

DATAFORSEO_ITEMS = DATAFORSEO_RESPONSE["tasks"][0]["result"][0]["items"]

USER_ID = uuid.uuid4()
SCRAPE_CACHE_ID = uuid.uuid4()
SEARCH_ID = uuid.uuid4()


def _make_db_rows_from_items(items):
    """Convert DataForSEO API items into dicts that look like DB rows from search_results."""
    rows = []
    for item in items:
        rows.append({
            "id": uuid.uuid4(),
            "scrape_cache_id": SCRAPE_CACHE_ID,
            "business_name": item.get("title"),
            "domain": item.get("domain"),
            "url": item.get("url"),
            "phone": item.get("phone"),
            "email": item.get("email"),
            "address": item.get("address"),
            "city": item.get("city"),
            "state": item.get("state"),
            "zip": item.get("zip"),
            "country": item.get("country_code"),
            "rating": item.get("rating", {}).get("value"),
            "reviews_count": item.get("rating", {}).get("votes_count"),
            "place_id": item.get("place_id"),
            "cid": item.get("cid"),
            "google_maps_url": item.get("url"),
            "category": item.get("category"),
            "additional_categories": json.dumps(item.get("additional_categories", [])),
            "category_ids": json.dumps(item.get("category_ids", [])),
            "is_claimed": item.get("is_claimed"),
            "verified": item.get("is_verified"),
            "photos_count": item.get("photos_count"),
            "main_image": item.get("main_image"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "price_level": item.get("price_level"),
            "work_hours": json.dumps(item.get("work_hours", {})),
            "business_status": item.get("business_status"),
            "rating_distribution": json.dumps(item.get("rating_distribution", {})),
            # Computed columns that the DB would normally generate
            "has_website": item.get("domain") is not None,
            "has_email": item.get("email") is not None,
            "has_phone": item.get("phone") is not None,
        })
    return rows


DB_ROWS = _make_db_rows_from_items(DATAFORSEO_ITEMS)

GEO_RESULT = {"lat": 40.7128, "lng": -74.006, "country_code": "US", "display_name": "New York, NY, USA"}


# ---- Pure function tests (no mocking needed) ----

from app.services.search_service import build_cache_key, apply_filters


class TestBuildCacheKey:
    def test_build_cache_key(self):
        key = build_cache_key("Dentist", "  New York  ", 13, False, "US")
        assert key == "dentist|new york|13|false|us"

    def test_build_cache_key_near_me(self):
        key = build_cache_key("Pizza", "Chicago", 14, True, "US")
        assert key == "pizza|chicago|14|true|us"

    def test_build_cache_key_empty_country(self):
        key = build_cache_key("cafe", "paris", 12, False)
        assert key == "cafe|paris|12|false|"


class TestApplyFilters:
    def test_no_filters_returns_all(self):
        result = apply_filters(DB_ROWS, {})
        assert len(result) == 5

    def test_has_email_yes(self):
        """Items with email: Manhattan Dental Care, Dr. Smith Orthodontics, Midtown Family Dentistry = 3"""
        result = apply_filters(DB_ROWS, {"has_email": "yes"})
        assert len(result) == 3
        for r in result:
            assert r["has_email"] is True

    def test_has_email_no(self):
        """Items without email: NYC Smile Clinic, Budget Dental Express = 2"""
        result = apply_filters(DB_ROWS, {"has_email": "no"})
        assert len(result) == 2
        for r in result:
            assert r["has_email"] is False

    def test_has_website_yes(self):
        """Items with domain: all except Budget Dental Express = 4"""
        result = apply_filters(DB_ROWS, {"has_website": "yes"})
        assert len(result) == 4
        for r in result:
            assert r["has_website"] is True

    def test_has_website_no(self):
        """Only Budget Dental Express has no website = 1"""
        result = apply_filters(DB_ROWS, {"has_website": "no"})
        assert len(result) == 1
        assert result[0]["business_name"] == "Budget Dental Express"

    def test_min_rating(self):
        """Rating >= 4.0: Manhattan (4.5), Dr. Smith (4.9), Midtown (4.2) = 3"""
        result = apply_filters(DB_ROWS, {"min_rating": 4.0})
        assert len(result) == 3
        for r in result:
            assert r["rating"] >= 4.0

    def test_min_reviews(self):
        """reviews_count >= 100: Manhattan (120), Dr. Smith (310) = 2"""
        result = apply_filters(DB_ROWS, {"min_reviews": 100})
        assert len(result) == 2

    def test_is_claimed_yes(self):
        """All except Budget Dental Express are claimed = 4"""
        result = apply_filters(DB_ROWS, {"is_claimed": "yes"})
        assert len(result) == 4

    def test_is_claimed_no(self):
        """Only Budget Dental Express is unclaimed = 1"""
        result = apply_filters(DB_ROWS, {"is_claimed": "no"})
        assert len(result) == 1

    def test_has_photos_yes(self):
        """All except Budget Dental Express (photos_count=0) = 4"""
        result = apply_filters(DB_ROWS, {"has_photos": "yes"})
        assert len(result) == 4

    def test_has_photos_no(self):
        """Only Budget Dental Express has 0 photos = 1"""
        result = apply_filters(DB_ROWS, {"has_photos": "no"})
        assert len(result) == 1

    def test_category_filter(self):
        """Only Dr. Smith is an Orthodontist = 1"""
        result = apply_filters(DB_ROWS, {"category": "Orthodontist"})
        assert len(result) == 1
        assert result[0]["business_name"] == "Dr. Smith Orthodontics"

    def test_combined_filters(self):
        """has_email=yes AND min_rating=4.5 → Manhattan (4.5) + Dr. Smith (4.9) = 2"""
        result = apply_filters(DB_ROWS, {"has_email": "yes", "min_rating": 4.5})
        assert len(result) == 2


# ---- Async tests (mock external deps) ----

@pytest.mark.asyncio
@patch("app.services.search_service.geocode", new_callable=AsyncMock)
async def test_search_calls_geocoder(mock_geocode):
    """Verify geocode is called with the location string."""
    mock_geocode.return_value = GEO_RESULT

    # We need to mock the rest too so search() doesn't blow up
    with patch("app.services.search_service.find_cached_scrape", new_callable=AsyncMock) as mock_cache, \
         patch("app.services.search_service.get_cached_results", new_callable=AsyncMock) as mock_results, \
         patch("app.services.search_service.get_balance", new_callable=AsyncMock) as mock_bal, \
         patch("app.services.search_service.deduct_credits", new_callable=AsyncMock) as mock_deduct, \
         patch("app.services.search_service.fetchrow", new_callable=AsyncMock) as mock_fetchrow:

        mock_cache.return_value = {"id": SCRAPE_CACHE_ID, "raw_result_count": 5}
        mock_results.return_value = DB_ROWS
        mock_bal.return_value = 999
        mock_deduct.return_value = 994
        mock_fetchrow.return_value = {"id": SEARCH_ID}

        from app.services.search_service import search
        await search(USER_ID, "dentist", "New York")

    mock_geocode.assert_called_once_with("New York")


@pytest.mark.asyncio
async def test_search_cache_hit_skips_api():
    """When cache exists, DataForSEO should NOT be called."""
    with patch("app.services.search_service.geocode", new_callable=AsyncMock) as mock_geocode, \
         patch("app.services.search_service.find_cached_scrape", new_callable=AsyncMock) as mock_cache, \
         patch("app.services.search_service.get_cached_results", new_callable=AsyncMock) as mock_results, \
         patch("app.services.search_service.dataforseo_client") as mock_dfs, \
         patch("app.services.search_service.get_balance", new_callable=AsyncMock) as mock_bal, \
         patch("app.services.search_service.deduct_credits", new_callable=AsyncMock) as mock_deduct, \
         patch("app.services.search_service.fetchrow", new_callable=AsyncMock) as mock_fetchrow:

        mock_geocode.return_value = GEO_RESULT
        mock_cache.return_value = {"id": SCRAPE_CACHE_ID, "raw_result_count": 5}
        mock_results.return_value = DB_ROWS
        mock_bal.return_value = 999
        mock_deduct.return_value = 994
        mock_fetchrow.return_value = {"id": SEARCH_ID}
        mock_dfs.search_maps = AsyncMock()

        from app.services.search_service import search
        await search(USER_ID, "dentist", "New York")

    mock_dfs.search_maps.assert_not_called()


@pytest.mark.asyncio
async def test_search_cache_miss_calls_api():
    """When no cache exists, DataForSEO should be called and results stored."""
    with patch("app.services.search_service.geocode", new_callable=AsyncMock) as mock_geocode, \
         patch("app.services.search_service.find_cached_scrape", new_callable=AsyncMock) as mock_cache, \
         patch("app.services.search_service.get_cached_results", new_callable=AsyncMock) as mock_results, \
         patch("app.services.search_service.dataforseo_client") as mock_dfs, \
         patch("app.services.search_service.store_scrape", new_callable=AsyncMock) as mock_store, \
         patch("app.services.search_service.get_balance", new_callable=AsyncMock) as mock_bal, \
         patch("app.services.search_service.deduct_credits", new_callable=AsyncMock) as mock_deduct, \
         patch("app.services.search_service.fetchrow", new_callable=AsyncMock) as mock_fetchrow:

        mock_geocode.return_value = GEO_RESULT
        mock_cache.return_value = None  # No cache
        mock_dfs.search_maps = AsyncMock(return_value=DATAFORSEO_RESPONSE)
        mock_store.return_value = SCRAPE_CACHE_ID
        mock_results.return_value = DB_ROWS
        mock_bal.return_value = 999
        mock_deduct.return_value = 994
        mock_fetchrow.return_value = {"id": SEARCH_ID}

        from app.services.search_service import search
        await search(USER_ID, "dentist", "New York")

    mock_dfs.search_maps.assert_called_once()
    mock_store.assert_called_once()


@pytest.mark.asyncio
async def test_search_applies_filters():
    """Filters should reduce the result count."""
    with patch("app.services.search_service.geocode", new_callable=AsyncMock) as mock_geocode, \
         patch("app.services.search_service.find_cached_scrape", new_callable=AsyncMock) as mock_cache, \
         patch("app.services.search_service.get_cached_results", new_callable=AsyncMock) as mock_results, \
         patch("app.services.search_service.get_balance", new_callable=AsyncMock) as mock_bal, \
         patch("app.services.search_service.deduct_credits", new_callable=AsyncMock) as mock_deduct, \
         patch("app.services.search_service.fetchrow", new_callable=AsyncMock) as mock_fetchrow:

        mock_geocode.return_value = GEO_RESULT
        mock_cache.return_value = {"id": SCRAPE_CACHE_ID, "raw_result_count": 5}
        mock_results.return_value = DB_ROWS
        mock_bal.return_value = 999
        mock_deduct.return_value = 996
        mock_fetchrow.return_value = {"id": SEARCH_ID}

        from app.services.search_service import search
        result = await search(USER_ID, "dentist", "New York", filters={"has_email": "yes"})

    # 3 items have email
    assert result["result_count"] == 3
    assert result["credits_used"] == 3


@pytest.mark.asyncio
async def test_search_deducts_credits():
    """Credits deducted should equal filtered_count."""
    with patch("app.services.search_service.geocode", new_callable=AsyncMock) as mock_geocode, \
         patch("app.services.search_service.find_cached_scrape", new_callable=AsyncMock) as mock_cache, \
         patch("app.services.search_service.get_cached_results", new_callable=AsyncMock) as mock_results, \
         patch("app.services.search_service.get_balance", new_callable=AsyncMock) as mock_bal, \
         patch("app.services.search_service.deduct_credits", new_callable=AsyncMock) as mock_deduct, \
         patch("app.services.search_service.fetchrow", new_callable=AsyncMock) as mock_fetchrow:

        mock_geocode.return_value = GEO_RESULT
        mock_cache.return_value = {"id": SCRAPE_CACHE_ID, "raw_result_count": 5}
        mock_results.return_value = DB_ROWS
        mock_bal.return_value = 999
        mock_deduct.return_value = 994
        mock_fetchrow.return_value = {"id": SEARCH_ID}

        from app.services.search_service import search
        await search(USER_ID, "dentist", "New York")

    # All 5 results, no filters → deduct 5
    mock_deduct.assert_called_once_with(USER_ID, 5, reference_id=SCRAPE_CACHE_ID)


@pytest.mark.asyncio
async def test_search_insufficient_credits_raises():
    """When balance < filtered_count, raise InsufficientCreditsError."""
    with patch("app.services.search_service.geocode", new_callable=AsyncMock) as mock_geocode, \
         patch("app.services.search_service.find_cached_scrape", new_callable=AsyncMock) as mock_cache, \
         patch("app.services.search_service.get_cached_results", new_callable=AsyncMock) as mock_results, \
         patch("app.services.search_service.get_balance", new_callable=AsyncMock) as mock_bal:

        mock_geocode.return_value = GEO_RESULT
        mock_cache.return_value = {"id": SCRAPE_CACHE_ID, "raw_result_count": 5}
        mock_results.return_value = DB_ROWS
        mock_bal.return_value = 2  # Only 2 credits, but 5 results

        from app.services.search_service import search, InsufficientCreditsError
        with pytest.raises(InsufficientCreditsError) as exc_info:
            await search(USER_ID, "dentist", "New York")

        assert exc_info.value.needed == 5
        assert exc_info.value.available == 2
