"""Tests for search_result_ids junction table population during search."""

import json
import uuid
from unittest.mock import AsyncMock, patch, call

import pytest

from tests.conftest import MOCK_USER_ID


def _make_raw_result(result_id, has_website=True, has_email=True, rating=4.5, reviews=100):
    return {
        "id": result_id,
        "scrape_cache_id": uuid.uuid4(),
        "business_name": "Test Biz",
        "has_website": has_website,
        "has_email": has_email,
        "has_phone": True,
        "rating": rating,
        "reviews_count": reviews,
        "is_claimed": True,
        "photos_count": 5,
        "category": "Plumber",
        "domain": "test.com" if has_website else None,
        "email": "a@b.com" if has_email else None,
        "phone": "555-0001",
    }


class TestSearchResultIdsStorage:
    @patch("app.services.search_service.execute", new_callable=AsyncMock)
    @patch("app.services.search_service.fetchrow", new_callable=AsyncMock)
    @patch("app.services.search_service.fetch", new_callable=AsyncMock)
    @patch("app.services.search_service.deduct_credits", new_callable=AsyncMock)
    @patch("app.services.search_service.get_balance", new_callable=AsyncMock)
    @patch("app.services.search_service.geocode", new_callable=AsyncMock)
    @patch("app.services.search_service.resolve_location")
    def test_search_stores_filtered_result_ids(
        self, mock_resolve, mock_geocode, mock_balance, mock_deduct,
        mock_fetch, mock_fetchrow, mock_execute
    ):
        cache_id = uuid.uuid4()
        search_id = uuid.uuid4()
        result_id_1 = uuid.uuid4()
        result_id_2 = uuid.uuid4()
        result_id_3 = uuid.uuid4()

        mock_geocode.return_value = {"lat": 40.7, "lng": -74.0, "country_code": "US"}
        mock_resolve.return_value = {"location_code": 2840, "language_code": "en"}
        mock_fetchrow.side_effect = [
            {"id": cache_id, "raw_result_count": 3},  # find_cached_scrape
            {"id": search_id},  # INSERT INTO searches RETURNING id
        ]
        mock_fetch.return_value = [
            _make_raw_result(result_id_1, has_website=True),
            _make_raw_result(result_id_2, has_website=True),
            _make_raw_result(result_id_3, has_website=False),
        ]
        mock_balance.return_value = 99
        mock_deduct.return_value = 97

        import asyncio
        from app.services.search_service import search

        result = asyncio.get_event_loop().run_until_complete(
            search(MOCK_USER_ID, "plumber", "NYC", filters={"has_website": "yes"})
        )

        # Verify search_result_ids INSERT was called for each filtered result
        execute_calls = [str(c) for c in mock_execute.call_args_list]
        junction_calls = [c for c in execute_calls if "search_result_ids" in c]
        assert len(junction_calls) == 2
